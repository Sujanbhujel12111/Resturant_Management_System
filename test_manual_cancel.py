import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import Order, OrderHistory, OrderHistoryItem, OrderHistoryPayment, User
from decimal import Decimal

# Get an order without payments
order = Order.objects.filter(payments__isnull=True).first()
if not order:
    order = Order.objects.annotate(payment_count=django.db.models.Count('payments')).filter(payment_count=0).first()

if order:
    print(f"Testing with order {order.order_id} (pk={order.id})")
    print(f"Payments: {order.payments.count()}")
    
    # Try to create it in history
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        
        print(f"Creating OrderHistory with user: {admin_user}")
        order_history = OrderHistory.objects.create(
            order_id=order.order_id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            order_type=order.order_type,
            status='cancelled',
            total_amount=order.total_amount,
            special_notes=order.special_notes,
            cancellation_reason="Test cancellation from script",
            table=order.table,
            completed_by=admin_user,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        print(f"✓ OrderHistory created: {order_history.id}")
        
        # Copy items
        for item in order.items.all():
            OrderHistoryItem.objects.create(
                order_history=order_history,
                item=item.item,
                quantity=item.quantity,
                price=item.price
            )
        print(f"✓ Copied {order.items.count()} items")
        
        # Copy payments
        for payment in order.payments.all():
            OrderHistoryPayment.objects.create(
                order_history=order_history,
                payment_method=payment.payment_method,
                amount=payment.amount,
                transaction_id=payment.transaction_id
            )
        print(f"✓ Copied {order.payments.count()} payments")
        
        # Delete original
        order.delete()
        print(f"✓ Deleted original order")
        
        # Verify
        cancelled = OrderHistory.objects.filter(status='cancelled')
        print(f"\nTotal cancelled orders now: {cancelled.count()}")
        for c in cancelled:
            print(f"  - {c.order_id}: {c.cancellation_reason}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No suitable order found")
