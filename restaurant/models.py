from django.db import models
import uuid
import random
from django.conf import settings
import datetime

def generate_order_id():
    """Generate a unique 8-digit order ID"""
    while True:
        order_id = str(random.randint(10000000, 99999999))
        # Check if this ID doesn't exist in Order or OrderHistory
        if not Order.objects.filter(order_id=order_id).exists() and not OrderHistory.objects.filter(order_id=order_id).exists():
            return order_id

class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    DEMAND_TIER_CHOICES = [
        ('high', 'High Demand (Tier 1)'),
        ('medium', 'Medium Demand (Tier 2)'),
        ('low', 'Low Demand (Tier 3)'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    preparation_area = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='menu_images/', blank=True)
    demand_tier = models.CharField(
        max_length=10,
        choices=DEMAND_TIER_CHOICES,
        default='medium',
        help_text="Demand tier calculated by K-Means clustering on order history"
    )
    order_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of times this item was ordered"
    )
    last_tier_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the demand tier was recalculated"
    )

    def __str__(self):
        return self.name

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=4)  # Provide a default value
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.number}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Cooking'),
        ('ready', 'Ready'),
        ('on_the_way', 'On The Way'),
        ('ready_to_pickup', 'Ready to Pickup'),
        ('served', 'Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_TYPE_CHOICES = [
        ('table', 'Table'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
    ]
    
    delivery_charge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Delivery charge for delivery orders"
    )

    order_id = models.CharField(max_length=8, default=generate_order_id, editable=False, unique=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    # Delivery address fields
    delivery_address = models.TextField(blank=True, null=True)
    delivery_landmark = models.CharField(max_length=255, blank=True, null=True)
    delivery_building = models.CharField(max_length=255, blank=True, null=True)
    delivery_unit = models.CharField(max_length=100, blank=True, null=True)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, default='unpaid')
    special_notes = models.TextField(blank=True, null=True)
    table = models.ForeignKey('Table', on_delete=models.SET_NULL, null=True, blank=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_orders')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"

    def move_to_history(self):
        """
        Moves a completed and paid order to order history.
        Returns the created OrderHistory instance if successful, None otherwise.
        """
        if self.status == 'completed' and self.payment_status == 'paid':
            try:
                # Only copy delivery_charge if it's a delivery order
                delivery_charge_to_copy = self.delivery_charge if self.order_type == 'delivery' else 0
                
                # First, create the OrderHistory instance
                order_history = OrderHistory.objects.create(
                    order_id=self.order_id,
                    customer_name=self.customer_name,
                    customer_phone=self.customer_phone,
                    order_type=self.order_type,
                    status=self.status,
                    total_amount=self.total_amount,
                    delivery_charge=delivery_charge_to_copy,
                    special_notes=self.special_notes or '',  # Provide empty string if None
                    table=self.table,
                    delivery_address=self.delivery_address,
                    delivery_landmark=self.delivery_landmark,
                    delivery_building=self.delivery_building,
                    delivery_unit=self.delivery_unit,
                    completed_by=self.completed_by,
                    created_at=self.created_at,
                    updated_at=self.updated_at
                )
                
                # Copy order items
                for order_item in self.items.all():
                    try:
                        OrderHistoryItem.objects.create(
                            order_history=order_history,
                            item=order_item.item,
                            quantity=order_item.quantity,
                            price=order_item.price
                        )
                    except Exception as e:
                        print(f"Error copying order item: {e}")
                
                # Copy payment information
                for payment in self.payments.all():
                    try:
                        OrderHistoryPayment.objects.create(
                            order_history=order_history,
                            payment_method=payment.payment_method,
                            amount=payment.amount,
                            transaction_id=payment.transaction_id
                        )
                    except Exception as e:
                        print(f"Error copying payment: {e}")
                
                # Only delete the original order after successfully copying everything
                # Copy status change logs into OrderHistoryStatus before deleting the order
                try:
                    from .models import OrderStatusLog, OrderHistoryStatus
                except Exception:
                    OrderStatusLog = None
                    OrderHistoryStatus = None

                if OrderStatusLog and OrderHistoryStatus:
                    for log in self.status_logs.all():
                        try:
                            OrderHistoryStatus.objects.create(
                                order_history=order_history,
                                previous_status=log.previous_status,
                                new_status=log.new_status,
                                changed_by=log.changed_by,
                                timestamp=log.timestamp
                            )
                        except Exception as e:
                            print(f"Error copying status log: {e}")

                # Delete the original order (and cascade-delete its logs)
                self.delete()
                
                return order_history
            except Exception as e:
                print(f"Error moving order to history: {e}")
                return None
        return None


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.item.name}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('fonepay', 'Fonepay'),
        ('bank', 'Bank'),
        ('khalti', 'Khalti'),
        ('esewa', 'Esewa'),
        ('imepay', 'Imepay'),
        ('connectips', 'Connectips'),
    ]

    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.payment_method} - {self.amount}'

class OrderHistory(models.Model):
    order_id = models.CharField(max_length=8, editable=False)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    order_type = models.CharField(max_length=20, choices=Order.ORDER_TYPE_CHOICES, default='table')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES, default='completed')
    payment_method = models.CharField(max_length=20, choices=Payment.PAYMENT_METHOD_CHOICES, default='cash')  # Changed from payment_status
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    special_notes = models.TextField(blank=True)
    # Preserve delivery address fields in history
    delivery_address = models.TextField(blank=True, null=True)
    delivery_landmark = models.CharField(max_length=255, blank=True, null=True)
    delivery_building = models.CharField(max_length=255, blank=True, null=True)
    delivery_unit = models.CharField(max_length=100, blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True, help_text="Reason for order cancellation")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Delivery charge for delivery orders"
    )
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_order_histories')

    def __str__(self):
        return f"Order History {self.order_id}"

    @property
    def payment_details(self):
        """Returns a list of payment details for this order"""
        payments = OrderHistoryPayment.objects.filter(order_history=self)
        return payments

    def revert_to_order(self, revert_status='served'):
        """
        Reverts an order from history back to the active Order table.
        Creates a new Order record with items and payments from history.
        Returns the created Order instance if successful, None otherwise.
        """
        try:
            # Create a new active Order with the history data
            new_order = Order.objects.create(
                order_id=self.order_id,
                customer_name=self.customer_name,
                customer_phone=self.customer_phone,
                order_type=self.order_type,
                status=revert_status,  # Revert to a previous status (e.g., 'served', 'ready')
                total_amount=self.total_amount,
                special_notes=self.special_notes,
                table=self.table,
                delivery_address=self.delivery_address,
                delivery_landmark=self.delivery_landmark,
                delivery_building=self.delivery_building,
                delivery_unit=self.delivery_unit,
                payment_status='unpaid',  # Reset payment status when reverting
                completed_by=None,  # Clear who completed it
            )
            
            # Copy order items from history
            for history_item in self.items.all():
                try:
                    OrderItem.objects.create(
                        order=new_order,
                        item=history_item.item,
                        quantity=history_item.quantity,
                        price=history_item.price
                    )
                except Exception as e:
                    print(f"Error copying order item back: {e}")
            
            # Copy payments from history (optional: copy or reset to 0)
            for history_payment in self.payments.all():
                try:
                    Payment.objects.create(
                        order=new_order,
                        payment_method=history_payment.payment_method,
                        amount=history_payment.amount,
                        transaction_id=history_payment.transaction_id,
                        edited_by=None
                    )
                except Exception as e:
                    print(f"Error copying payment back: {e}")
            
            # Delete the history record (and cascade-delete its items/payments via related names)
            self.delete()
            
            return new_order
        except Exception as e:
            print(f"Error reverting order from history: {e}")
            return None

class OrderHistoryPayment(models.Model):
    order_history = models.ForeignKey(OrderHistory, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=50, choices=Payment.PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.payment_method} - {self.amount}'


class OrderHistoryItem(models.Model):
    order_history = models.ForeignKey(OrderHistory, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.item.name} (Order History)"


# Add back status log models (minimal form) so migrations that remove / copy these can run reliably.
class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, related_name='status_logs', on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50, blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_id}: {self.previous_status} -> {self.new_status} @ {self.timestamp}"

class OrderHistoryStatus(models.Model):
    order_history = models.ForeignKey(OrderHistory, related_name='status_logs', on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50, blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.order_history.order_id}: {self.previous_status} -> {self.new_status} @ {self.timestamp}"