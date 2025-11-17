from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Table, Category, MenuItem, Order, OrderItem, Payment, OrderHistory, OrderHistoryPayment
from .forms import MenuItemForm, CategoryForm, OrderForm, OrderItemForm, PaymentForm
import json
from django.db.models import Sum
from django.contrib import messages
from datetime import date
from django.shortcuts import render, get_object_or_404
from django.forms import modelformset_factory
from .models import Table, MenuItem, OrderItem
from .forms import OrderForm, OrderItemForm
from django.db import models
from django.contrib.auth import views as auth_views
import qrcode
from io import BytesIO


class LoginView(auth_views.LoginView):
    template_name = 'home/login.html'

class LogoutView(auth_views.LogoutView):
    template_name = 'home/logout.html'


@login_required
def menu_view(request):
    # Pass all categories (active and inactive) so staff can manage visibility
    categories = Category.objects.all().prefetch_related('menuitem_set')
    return render(request, 'restaurant/menu.html', {'categories': categories})

@login_required
def public_menu_view(request):
    # Show only items from active categories that are available
    categories = Category.objects.filter(is_active=True).prefetch_related('menuitem_set')
    menu_items = MenuItem.objects.filter(is_available=True, category__is_active=True)
    return render(request, 'restaurant/public_menu.html', {
        'categories': categories,
        'menu_items': menu_items
    })

@login_required
def generate_qr_code(request):
    menu_url = request.build_absolute_uri(reverse('restaurant:public_menu_view'))
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(menu_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer, content_type="image/png")

@login_required
def dashboard_view(request):
    today = date.today()
    pending_orders = Order.objects.exclude(status__in=['completed', 'cancelled']).count()
    active_tables = Table.objects.filter(status='occupied').count()
    total_menu_items = MenuItem.objects.filter(is_available=True).count()
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    context = {
        'pending_orders': pending_orders,
        'active_tables': active_tables,
        'total_menu_items': total_menu_items,
        'today_revenue': today_revenue,
        'orders': recent_orders,
    }
    return render(request, 'restaurant/dashboard.html', context)

@login_required
def kitchen_view(request):
    # Show active orders for the kitchen station. Include pending and preparing orders
    # so staff can see incoming orders and start preparing them. Exclude completed/cancelled.
    orders = Order.objects.exclude(status__in=['completed', 'cancelled']).order_by('created_at')
    return render(request, 'restaurant/kitchen.html', {'orders': orders})


@login_required
def kitchen_orders_api(request):
    """Return JSON list of active orders for the kitchen board (used by AJAX polling)."""
    orders_qs = Order.objects.exclude(status__in=['completed', 'cancelled']).order_by('created_at')
    orders_list = []
    for order in orders_qs:
        orders_list.append({
            'id': order.id,
            'order_id': order.order_id,
            'type': f"table #{order.table.number}" if order.table else ("Takeaway" if order.order_type == 'takeaway' else "Delivery"),
            'amount': float(order.total_amount or 0),
            'status': order.status,
            'items': order.items.count(),
        })
    return JsonResponse({'orders': orders_list})

@login_required
def place_order(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    OrderItemFormSet = modelformset_factory(OrderItem, form=OrderItemForm, extra=1)
    # Show only available items from active categories
    import json
    menu_items_qs = MenuItem.objects.filter(is_available=True, category__is_active=True).select_related('category')
    menu_items = list(menu_items_qs.values('id', 'name', 'price', 'category_id', 'category__name'))
    for item in menu_items:
        if isinstance(item['price'], Decimal):
            item['price'] = float(item['price'])
    menu_items_json = json.dumps(menu_items)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, queryset=OrderItem.objects.none())

        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            order.table = table
            order.status = 'pending'
            total_amount = 0

            # First save the order
            order.save()

            # Then save order items and calculate total
            for form in formset:
                if form.cleaned_data:  # Check if form has data
                    order_item = form.save(commit=False)
                    menu_item = MenuItem.objects.get(id=order_item.item.id)
                    order_item.price = menu_item.price
                    order_item.order = order
                    order_item.save()
                    
                    # Calculate item total and add to order total
                    item_total = order_item.price * order_item.quantity
                    total_amount += item_total

            # Update order with calculated total
            order.total_amount = total_amount
            order.save()

            return redirect('restaurant:order_list')

    else:
        order_form = OrderForm()
        formset = OrderItemFormSet(queryset=OrderItem.objects.none())

    return render(request, 'restaurant/place_order.html', {
        'table': table,
        'order_form': order_form,
        'formset': formset,
        'menu_items_json': menu_items_json,
    })


@login_required
@login_required
def place_order_takeaway(request):
    OrderItemFormSet = modelformset_factory(OrderItem, form=OrderItemForm, extra=1)
    # Show only available items from active categories
    import json
    menu_items_qs = MenuItem.objects.filter(is_available=True, category__is_active=True).select_related('category')
    menu_items = list(menu_items_qs.values('id', 'name', 'price', 'category_id', 'category__name'))
    # Convert Decimal price to float for JSON serialization
    for item in menu_items:
        if isinstance(item['price'], Decimal):
            item['price'] = float(item['price'])
    menu_items_json = json.dumps(menu_items)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, queryset=OrderItem.objects.none())

        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            order.order_type = 'takeaway'
            order.status = 'pending'
            order.save()

            total_amount = 0  # Initialize total_amount

            # Then save order items and calculate total
            for form in formset:
                if form.cleaned_data:  # Check if form has data
                    order_item = form.save(commit=False)
                    menu_item = MenuItem.objects.get(id=order_item.item.id)
                    order_item.price = menu_item.price
                    order_item.order = order
                    order_item.save()
                    
                    # Calculate item total and add to order total
                    item_total = order_item.price * order_item.quantity
                    total_amount += item_total

            # Update order with calculated total
            order.total_amount = total_amount
            order.save()

            return redirect('restaurant:order_list')

    else:
        order_form = OrderForm()
        formset = OrderItemFormSet(queryset=OrderItem.objects.none())

    return render(request, 'restaurant/place_order_takeaway.html', {
        'order_form': order_form,
        'formset': formset,
        'menu_items_json': menu_items_json,
    })

@login_required
def place_order_delivery(request):
    OrderItemFormSet = modelformset_factory(OrderItem, form=OrderItemForm, extra=1)
    # Show only available items from active categories
    import json
    menu_items_qs = MenuItem.objects.filter(is_available=True, category__is_active=True).select_related('category')
    menu_items = list(menu_items_qs.values('id', 'name', 'price', 'category_id', 'category__name'))
    for item in menu_items:
        if isinstance(item['price'], Decimal):
            item['price'] = float(item['price'])
    menu_items_json = json.dumps(menu_items)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, queryset=OrderItem.objects.none())
        delivery_charge = int(request.POST.get('delivery_charge', 100))  # Get delivery charge from form

        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            order.order_type = 'delivery'
            order.status = 'pending'
            order.delivery_charge = delivery_charge  # Save delivery charge
            order.save()

            total_amount = 0

            for form in formset:
                if form.cleaned_data:
                    order_item = form.save(commit=False)
                    menu_item = MenuItem.objects.get(id=order_item.item.id)
                    order_item.price = menu_item.price
                    order_item.order = order
                    order_item.save()
                    
                    item_total = order_item.price * order_item.quantity
                    total_amount += item_total

            # Save the base total amount (without delivery charge)
            order.total_amount = total_amount
            order.save()

            return redirect('restaurant:order_list')

    else:
        order_form = OrderForm()
        formset = OrderItemFormSet(queryset=OrderItem.objects.none())

    return render(request, 'restaurant/place_order_delivery.html', {
        'order_form': order_form,
        'formset': formset,
        'menu_items_json': menu_items_json,
    })

@login_required
def close_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = 'completed'
        order.payment_status = 'paid'  # Assuming payment is settled here
        # Record who closed/completed the order when using this path
        order.completed_by = request.user
        order.save()
        order.move_to_history()
        return redirect('restaurant:order_list')
    return render(request, 'restaurant/close_order.html', {'order': order})


@login_required
def payment_success(request):
    return render(request, 'restaurant/payment_success.html')

@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        # map UI-friendly aliases to model status values
        status_aliases = {
            'cooking': 'preparing',
            'cook': 'preparing',
            'ready': 'ready',
            'complete': 'completed',
            'completed': 'completed'
        }
        normalized = status_aliases.get(status, (status or '').strip())

        # Define allowed statuses per order type (server-side authoritative)
        allowed_statuses_by_type = {
            'delivery': ['pending', 'preparing', 'ready', 'on_the_way', 'completed', 'cancelled'],
            'takeaway': ['pending', 'preparing', 'ready_to_pickup', 'completed', 'cancelled'],
            'table': ['pending', 'preparing', 'ready', 'served', 'completed', 'cancelled'],
            None: list(dict(Order.ORDER_STATUS_CHOICES).keys()),
        }

        allowed_for_type = allowed_statuses_by_type.get(order.order_type, allowed_statuses_by_type[None])

        # Validate normalized status is allowed for this order type
        if normalized in allowed_for_type:
            # If attempting to mark completed, ensure payments cover total
            if normalized == 'completed':
                # calculate required amount (include delivery charge)
                required = order.total_amount
                if order.order_type == 'delivery':
                    required = required + (order.delivery_charge or 0)

                paid = order.payments.aggregate(total=Sum('amount'))['total'] or 0
                # use Decimal comparison if needed
                try:
                    from decimal import Decimal
                    paid_val = Decimal(paid)
                    required_val = Decimal(required)
                except Exception:
                    paid_val = paid
                    required_val = required

                # Check payment sufficiency
                if paid_val >= required_val:
                    order.status = 'completed'
                    order.payment_status = 'paid'
                    order.completed_by = request.user  # Track who completed the order
                    order.save()
                    # Move to history (this will delete the order if move_to_history succeeds)
                    order_history = None
                    try:
                        order_history = order.move_to_history()
                        if order_history:
                            messages.success(request, f'Order {order.order_id} completed and moved to history by {request.user.get_full_name() or request.user.username}.')
                        else:
                            messages.success(request, f'Order {order.order_id} marked completed by {request.user.get_full_name() or request.user.username}.')
                    except Exception as e:
                        # If move_to_history fails, keep order and report error
                        messages.error(request, f'Order marked completed but failed to move to history: {e}')
                    # If moved to history, later redirect to order history details; otherwise fall through
                    # NOTE: don't return here so final redirect logic can choose appropriate destination
                else:
                    messages.error(request, 'Cannot complete order: payments are not settled.')
                    # keep order in its current state
                    return redirect(request.META.get('HTTP_REFERER', reverse('restaurant:order_list')))
            else:
                order.status = normalized
                order.save()
                messages.success(request, f'Order {order.order_id} status updated to {order.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status')
    # Redirect back to the referring page when possible so UX remains on the same view
    # Decide redirect destination: if the requested status is 'completed' or 'cancelled',
    # send the user to the order details (or order history if the order was moved).
    referer = request.META.get('HTTP_REFERER')
    if normalized in ('completed', 'cancelled'):
        # If the order was moved to history, redirect to the history details view
        try:
            # If order still exists, redirect to order details; otherwise, go to order history
            if Order.objects.filter(order_id=order.order_id).exists():
                return redirect(reverse('restaurant:order_details', kwargs={'order_id': order.order_id}))
            else:
                # Order likely moved to history — redirect to history details
                return redirect(reverse('restaurant:order_history_details', kwargs={'order_id': order.order_id}))
        except Exception:
            # Fallback: try referer, then order list
            if referer:
                return redirect(referer)
            return redirect('restaurant:order_list')

    # For all other status updates, return to the referring page when possible
    if referer:
        return redirect(referer)
    # Final fallback to order list
    return redirect('restaurant:order_list')


@login_required
def cancel_order(request, pk):
    """Cancel an order with confirmation. Expects POST. Checks settled payments and moves to history."""
    import logging
    from decimal import Decimal
    from django.db import transaction
    
    logger = logging.getLogger(__name__)
    logger.info(f"cancel_order view called with pk={pk}, method={request.method}")
    
    order = get_object_or_404(Order, pk=pk)
    logger.info(f"Order retrieved: {order.order_id}")
    
    # Check if there are settled payments (all payments are settled by default)
    settled_payments = order.payments.all()
    settled_amount = sum((Decimal(p.amount) for p in settled_payments), Decimal('0'))
    logger.info(f"Order {order.order_id} has settled amount: {settled_amount}")
    
    if request.method == 'POST':
        logger.info(f"POST request for cancelling order {order.order_id}")
        # Prevent cancellation if there are settled payments
        if settled_amount > 0:
            messages.error(
                request, 
                f'Cannot cancel order with settled payments (Rs.{settled_amount}). '
                'Please clear the settled amount first or contact support.'
            )
            logger.warning(f"Cannot cancel {order.order_id} - has settled payments")
            return redirect('restaurant:order_details', order_id=order.order_id)
        
        # Get cancellation reason from form
        cancellation_reason = request.POST.get('cancellation_reason', '').strip()
        logger.info(f"Cancellation reason: {cancellation_reason}")
        
        # Move order to history with cancellation status and reason
        try:
            with transaction.atomic():
                logger.info(f"Creating OrderHistory for {order.order_id}")
                order_history = OrderHistory.objects.create(
                    order_id=order.order_id,
                    customer_name=order.customer_name,
                    customer_phone=order.customer_phone,
                    order_type=order.order_type,
                    status='cancelled',
                    total_amount=order.total_amount,
                    special_notes=order.special_notes,
                    cancellation_reason=cancellation_reason,
                    table=order.table,
                    completed_by=request.user,
                    created_at=order.created_at,
                    updated_at=order.updated_at
                )
                logger.info(f"OrderHistory created successfully: {order_history.id}")
                
                # Copy order items to history
                items_count = 0
                for order_item in order.items.all():
                    try:
                        OrderHistoryItem.objects.create(
                            order_history=order_history,
                            item=order_item.item,
                            quantity=order_item.quantity,
                            price=order_item.price
                        )
                        items_count += 1
                    except Exception as e:
                        logger.error(f"Error copying order item: {e}")
                logger.info(f"Copied {items_count} items to history")
                
                # Copy payment information to history
                payments_count = 0
                for payment in order.payments.all():
                    try:
                        OrderHistoryPayment.objects.create(
                            order_history=order_history,
                            payment_method=payment.payment_method,
                            amount=payment.amount,
                            transaction_id=payment.transaction_id
                        )
                        payments_count += 1
                    except Exception as e:
                        logger.error(f"Error copying payment: {e}")
                logger.info(f"Copied {payments_count} payments to history")
                
                # Success - delete the original order now that everything is copied
                order_id_backup = order.order_id
                order.delete()
                logger.info(f"Deleted original order {order_id_backup}")
            
            reason_text = f" - Reason: {cancellation_reason}" if cancellation_reason else ""
            messages.success(
                request, 
                f'Order {order_id_backup} cancelled and moved to history by {request.user.get_full_name() or request.user.username}.{reason_text}'
            )
            return redirect('restaurant:order_list')
        except Exception as e:
            logger.exception(f"Error cancelling order {order.order_id}: {e}")
            messages.error(request, f'Error cancelling order: {str(e)}')
            return redirect('restaurant:order_details', order_id=order.order_id)
    
    # GET request shouldn't happen normally, but just in case, redirect back
    return redirect('restaurant:order_details', order_id=order.order_id)

@login_required
def process_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.edited_by = request.user
            payment.save()
            return redirect('restaurant:order_details', order_id=order.order_id)
    else:
        form = PaymentForm()
    return render(request, 'restaurant/process_payment.html', {
        'form': form,
        'order': order,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES
    })

@login_required
def edit_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        payment.payment_method = data.get('payment_method')
        payment.amount = data.get('amount')
        payment.transaction_id = data.get('transaction_id')
        payment.edited_by = request.user
        payment.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from decimal import Decimal
from .models import Order, MenuItem, OrderItem

@login_required
def add_order_item(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, order_id=order_id)
            
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))
            
            if quantity < 1:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Quantity must be positive'
                }, status=400)
            
            menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
            
            # Check if item already exists in order
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                item=menu_item,
                defaults={
                    'quantity': quantity,
                    'price': menu_item.price
                }
            )
            
            if not created:
                order_item.quantity = quantity
                order_item.save()
            
            # Recalculate order total
            order_items = order.items.all()
            total_amount = sum(item.price * item.quantity for item in order_items)
            order.total_amount = total_amount
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Item added successfully',
                'new_total': str(total_amount),
                'item_html': {
                    'name': menu_item.name,
                    'quantity': order_item.quantity,
                    'price': str(menu_item.price),
                    'total': str(order_item.price * order_item.quantity),
                    'item_id': order_item.id
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)



@login_required
def remove_order_item(request, order_id, item_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id)
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        
        try:
            # Calculate the reduction in total amount
            reduction = order_item.price * order_item.quantity
            
            # Delete the order item
            order_item.delete()
            
            # Update the order's total amount
            order.total_amount -= reduction
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'new_total': str(order.total_amount)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@login_required
def update_order_items(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == 'POST':
        try:
            total_amount = 0
            for item in order.items.all():
                quantity = request.POST.get(f'quantity_{item.id}')
                if quantity is not None:
                    item.quantity = int(quantity)
                    item.save()
                    total_amount += item.price * item.quantity
            
            order.total_amount = total_amount
            order.save()
            return JsonResponse({'success': True, 'new_total': str(total_amount)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def transaction_history(request):
    orders = OrderHistory.objects.all().order_by('-created_at')
    context = {
        'orders': orders,
        'payment_method_choices': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'restaurant/transaction_history.html', context)

from django.http import JsonResponse

def get_order_details(request, order_id):
    # `order_id` here is the custom `order_id` field (8-digit string), not PK
    order = get_object_or_404(Order, order_id=order_id)
    completed_by = None
    if order.completed_by:
        completed_by = order.completed_by.get_full_name() or getattr(order.completed_by, 'username', None)

    response_data = {
        'order_id': order.order_id,
        'customer_name': getattr(order, 'customer_name', None),
        'customer_phone': getattr(order, 'customer_phone', None),
        'order_type': order.order_type,
        'table': {'number': order.table.number} if order.table else None,
        'completed_by': completed_by,
        'total_amount': float(order.total_amount),
        'payment_status': order.payment_status,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None,
        'special_notes': order.special_notes,
    }
    return JsonResponse(response_data)

@login_required
def order_details(request, order_id):
    from decimal import Decimal
    order = get_object_or_404(Order, order_id=order_id)
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True)
    
    # Calculate settled payments amount (all payments are settled)
    settled_payments = order.payments.all()
    settled_amount = sum((Decimal(p.amount) for p in settled_payments), Decimal('0'))
    
    context = {
        'order': order,
        'categories': categories,
        'menu_items': menu_items,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
        'settled_amount': settled_amount,
        'has_settled_payments': settled_amount > 0,
    }
    return render(request, 'restaurant/order_detail.html', context)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import OrderHistory, OrderHistoryItem



@login_required
def order_history_details(request, order_id):
    try:
        order = get_object_or_404(OrderHistory, order_id=order_id)
        
        # Get all order items
        order_items = order.items.all().select_related('item')
        items_data = []
        for item in order_items:
            try:
                item_data = {
                    'item_name': item.item.name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total': float(item.price * item.quantity)
                }
                items_data.append(item_data)
            except Exception as e:
                print(f"Error processing item: {e}")
        
        # Get payment details
        payment_data = []
        payment_method_dict = dict(Payment.PAYMENT_METHOD_CHOICES)
        for payment in order.payment_details:
            payment_data.append({
                'method': payment_method_dict.get(payment.payment_method, 'Unknown'),
                'amount': float(payment.amount),
                'transaction_id': payment.transaction_id
            })
        
        # Add table information if it's a table order
        table_data = None
        if order.order_type == 'table' and order.table:
            table_data = {
                'number': order.table.number,
                'capacity': order.table.capacity
            }
        
        data = {
            'order_id': str(order.order_id),
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'order_type': order.order_type,
            'table': table_data,
            'total_amount': float(order.total_amount),
            'payments': payment_data,
            # Prefer full name if available, otherwise fall back to username
            'completed_by': (order.completed_by.get_full_name() if (order.completed_by and order.completed_by.get_full_name()) else (order.completed_by.username if order.completed_by else None)),
            'special_notes': order.special_notes,
            'cancellation_reason': order.cancellation_reason,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'items': items_data
        }
        
        return JsonResponse(data)
    except Exception as e:
        print(f"Error in order_history_details: {e}")
        return JsonResponse({
            'error': 'Failed to fetch order details',
            'message': str(e)
        }, status=500)



from .forms import TableForm


@login_required
def order_update_notes(request, order_id):
    """AJAX endpoint to update special_notes on an OrderHistory record.
    Expects JSON POST: { "notes": "..." }
    Returns JSON { success: true, notes: "..." }
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        payload = {}
        if request.body:
            try:
                payload = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
            except Exception:
                # if body is not JSON, try to parse as form-encoded
                try:
                    payload = request.POST.dict()
                except Exception:
                    payload = {}

        notes = (payload.get('notes') or '').strip()
        oh = get_object_or_404(OrderHistory, order_id=order_id)
        oh.special_notes = notes
        oh.save()
        return JsonResponse({'success': True, 'notes': notes})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

class TableListView(LoginRequiredMixin, ListView):
    model = Table
    template_name = 'restaurant/table_list.html'
    context_object_name = 'tables'

    def get_queryset(self):
        # Annotate each table with occupied status based on pending orders
        tables = Table.objects.all()
        table_ids_with_pending_orders = set(
            Order.objects.filter(
                table__isnull=False,
                status__in=['pending', 'preparing', 'ready', 'served']
            ).values_list('table_id', flat=True)
        )
        for table in tables:
            table.is_occupied = table.id in table_ids_with_pending_orders
        return tables

class TableCreateView(LoginRequiredMixin, CreateView):
    model = Table
    form_class = TableForm
    template_name = 'restaurant/table_form.html'
    success_url = reverse_lazy('restaurant:table_list')

class TableUpdateView(LoginRequiredMixin, UpdateView):
    model = Table
    form_class = TableForm
    template_name = 'restaurant/table_form.html'
    success_url = reverse_lazy('restaurant:table_list')

class TableDeleteView(LoginRequiredMixin, DeleteView):
    model = Table
    template_name = 'restaurant/table_confirm_delete.html'
    success_url = reverse_lazy('restaurant:table_list')

class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'restaurant/menuitem_list.html'
    context_object_name = 'menu_items'

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/menuitem_form.html'
    success_url = reverse_lazy('restaurant:menuitem_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter out inactive categories
        form.fields['category'].queryset = Category.objects.filter(is_active=True)
        return form

from django.core.paginator import Paginator

def transaction_history(request):
    # Server-side filtering for transaction history (date range, type, search) and pagination
    orders_qs = OrderHistory.objects.all().order_by('-created_at')

    # Filters from query params
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    order_type = request.GET.get('order_type')
    status = request.GET.get('status')  # New status filter
    try:
        entries = int(request.GET.get('entries', 10))
    except Exception:
        entries = 10

    if q:
        from django.db.models import Q
        orders_qs = orders_qs.filter(
            Q(order_id__icontains=q) | Q(customer_name__icontains=q) | Q(customer_phone__icontains=q)
        )

    from datetime import datetime
    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            orders_qs = orders_qs.filter(created_at__date__gte=sd)
        except Exception:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            orders_qs = orders_qs.filter(created_at__date__lte=ed)
        except Exception:
            pass

    if order_type:
        orders_qs = orders_qs.filter(order_type=order_type)
    
    if status:
        orders_qs = orders_qs.filter(status=status)

    paginator = Paginator(orders_qs, entries)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    # Preserve other query params for pagination links
    from urllib.parse import urlencode
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')
    params_str = params.urlencode()

    context = {
        'orders': orders,
        'payment_method_choices': Payment.PAYMENT_METHOD_CHOICES,
        'params': params_str,
        'q': q,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'order_type': order_type or '',
        'status': status or '',
        'entries': str(entries),
    }
    return render(request, 'restaurant/transaction_history.html', context)


@login_required
def export_orders_csv(request):
    """Export filtered OrderHistory rows as CSV (opens in Excel)."""
    orders_qs = OrderHistory.objects.all().order_by('-created_at')

    # Apply same filters as transaction_history
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    order_type = request.GET.get('order_type')
    status = request.GET.get('status')

    if q:
        from django.db.models import Q
        orders_qs = orders_qs.filter(
            Q(order_id__icontains=q) | Q(customer_name__icontains=q) | Q(customer_phone__icontains=q)
        )

    from datetime import datetime
    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            orders_qs = orders_qs.filter(created_at__date__gte=sd)
        except Exception:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            orders_qs = orders_qs.filter(created_at__date__lte=ed)
        except Exception:
            pass

    if order_type:
        orders_qs = orders_qs.filter(order_type=order_type)
    if status:
        orders_qs = orders_qs.filter(status=status)

    # Prepare CSV
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaction_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Phone', 'Type', 'Table', 'Status', 'Total Amount', 'Created At', 'Updated At', 'Notes'])
    for o in orders_qs:
        table_num = o.table.number if getattr(o, 'table', None) else ''
        writer.writerow([
            smart_str(o.order_id),
            smart_str(o.customer_name),
            smart_str(o.customer_phone),
            smart_str(o.order_type),
            smart_str(table_num),
            smart_str(o.status),
            smart_str(o.total_amount),
            o.created_at.isoformat() if o.created_at else '',
            o.updated_at.isoformat() if o.updated_at else '',
            smart_str(o.special_notes or '')
        ])

    return response


@login_required
def export_orders_pdf(request):
    """Export filtered OrderHistory rows as a professionally formatted PDF with tables.
    Requires `reportlab` package. If not available, returns 501 with installation hint.
    """
    orders_qs = OrderHistory.objects.all().order_by('-created_at')

    # Reuse same filtering logic
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    order_type = request.GET.get('order_type')
    status = request.GET.get('status')

    if q:
        from django.db.models import Q
        orders_qs = orders_qs.filter(
            Q(order_id__icontains=q) | Q(customer_name__icontains=q) | Q(customer_phone__icontains=q)
        )

    from datetime import datetime
    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            orders_qs = orders_qs.filter(created_at__date__gte=sd)
        except Exception:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            orders_qs = orders_qs.filter(created_at__date__lte=ed)
        except Exception:
            pass

    if order_type:
        orders_qs = orders_qs.filter(order_type=order_type)
    if status:
        orders_qs = orders_qs.filter(status=status)

    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except Exception:
        return HttpResponse(
            'PDF export requires the `reportlab` package. Install with: pip install reportlab',
            status=501,
            content_type='text/plain'
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Header style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Data style
    data_style = ParagraphStyle(
        'DataStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT
    )
    
    # Add title
    elements.append(Paragraph('Transaction History Report', title_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Add filter info if any
    filter_info = []
    if q:
        filter_info.append(f"<b>Search:</b> {q}")
    if start_date or end_date:
        date_range = f"{start_date or 'N/A'} to {end_date or 'N/A'}"
        filter_info.append(f"<b>Date Range:</b> {date_range}")
    if order_type:
        filter_info.append(f"<b>Order Type:</b> {order_type}")
    if status:
        filter_info.append(f"<b>Status:</b> {status}")
    
    if filter_info:
        filter_text = " | ".join(filter_info)
        elements.append(Paragraph(f"<i>{filter_text}</i>", data_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Prepare table data
    table_data = [
        ['Order ID', 'Customer', 'Phone', 'Type', 'Table', 'Status', 'Amount', 'Created At']
    ]
    
    for o in orders_qs:
        table_num = str(o.table.number) if getattr(o, 'table', None) else '-'
        created_str = o.created_at.strftime('%Y-%m-%d %H:%M') if o.created_at else ''
        table_data.append([
            str(o.order_id),
            str(o.customer_name or ''),
            str(o.customer_phone or ''),
            str(o.order_type or ''),
            table_num,
            str(o.status or ''),
            f"Rs.{o.total_amount}",
            created_str
        ])
    
    # Create table with styling
    table = Table(table_data, colWidths=[1.0*inch, 1.2*inch, 0.9*inch, 0.7*inch, 0.5*inch, 0.8*inch, 0.7*inch, 1.0*inch])
    table.setStyle(TableStyle([
        # Header row style
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    from datetime import datetime as dt
    footer_text = f"<i>Report generated on {dt.now().strftime('%Y-%m-%d %H:%M:%S')} | Total records: {len(table_data) - 1}</i>"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={'Content-Disposition': 'attachment; filename="transaction_history.pdf"'})


class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/menuitem_form.html'
    success_url = reverse_lazy('restaurant:menuitem_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter out inactive categories but include the current category if inactive
        form.fields['category'].queryset = Category.objects.filter(
            models.Q(is_active=True) | models.Q(pk=self.object.category_id)
        )
        return form

class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'restaurant/menuitem_confirm_delete.html'
    success_url = reverse_lazy('restaurant:menuitem_list')

class MenuItemDetailView(LoginRequiredMixin, DetailView):
    model = MenuItem
    template_name = 'restaurant/menuitem_detail.html'
    context_object_name = 'menu_item'

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'restaurant/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'restaurant/category_form.html'
    success_url = reverse_lazy('restaurant:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'restaurant/category_form.html'
    success_url = reverse_lazy('restaurant:category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'restaurant/category_confirm_delete.html'
    success_url = reverse_lazy('restaurant:category_list')

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'restaurant/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Show all active orders. Exclude completed+paid and cancelled orders.
        # Keep completed orders if payment pending.
        from django.db.models import Q
        return Order.objects.exclude(
            Q(status='completed', payment_status='paid') | Q(status='cancelled')
        ).order_by('-created_at')