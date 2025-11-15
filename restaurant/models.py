from django.db import models
import uuid
import random
from django.contrib.auth.models import User
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
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    preparation_area = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='menu_images/', blank=True)

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
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, default='unpaid')
    special_notes = models.TextField(blank=True, null=True)
    table = models.ForeignKey('Table', on_delete=models.SET_NULL, null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_orders')
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
                # First, create the OrderHistory instance
                order_history = OrderHistory.objects.create(
                    order_id=self.order_id,
                    customer_name=self.customer_name,
                    customer_phone=self.customer_phone,
                    order_type=self.order_type,
                    status=self.status,
                    total_amount=self.total_amount,
                    special_notes=self.special_notes,
                    table=self.table,
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
        ('ipay', 'Ipay'),
        ('prabhu', 'Prabhu'),
        ('esewa', 'Esewa'),
        ('imepay', 'Imepay'),
        ('connectips', 'Connectips'),
        ('sct', 'SCT'),
        ('qr_code', 'QR Code'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

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
    cancellation_reason = models.TextField(blank=True, null=True, help_text="Reason for order cancellation")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_order_histories')

    def __str__(self):
        return f"Order History {self.order_id}"

    @property
    def payment_details(self):
        """Returns a list of payment details for this order"""
        payments = OrderHistoryPayment.objects.filter(order_history=self)
        return payments

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