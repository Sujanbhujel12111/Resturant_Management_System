import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import Order
from decimal import Decimal

print("Orders with NO payments (cancel form should show):")
for order in Order.objects.all()[:10]:
    payments = order.payments.all()
    settled = sum((Decimal(p.amount) for p in payments), Decimal('0'))
    if settled == 0:
        print(f"  Order {order.order_id} ({order.id}): {len(payments)} payments, should show cancel form ✓")

print("\nOrders with payments (warning shown instead):")
for order in Order.objects.all()[:10]:
    payments = order.payments.all()
    settled = sum((Decimal(p.amount) for p in payments), Decimal('0'))
    if settled > 0:
        print(f"  Order {order.order_id} ({order.id}): Rs.{settled}, warning shown")
