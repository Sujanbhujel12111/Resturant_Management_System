import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import OrderHistory, Order, Payment
from decimal import Decimal

print("Total Order objects:", Order.objects.count())
print("Total OrderHistory objects:", OrderHistory.objects.count())

print("\nChecking first 3 active orders for payments:")
for order in Order.objects.all()[:3]:
    payments = order.payments.all()
    total_paid = sum((Decimal(p.amount) for p in payments), Decimal('0'))
    print(f"  Order {order.order_id}: {payments.count()} payments, total={total_paid}")
    for p in payments:
        print(f"    - {p.payment_method}: {p.amount}")

print("\nCancelled orders in history:")
cancelled = OrderHistory.objects.filter(status='cancelled')
print(f"Count: {cancelled.count()}")
for order in cancelled:
    print(f"  - Order {order.order_id}: {order.cancellation_reason}")

print("\nAll orders in history (last 5):")
for order in OrderHistory.objects.all().order_by('-created_at')[:5]:
    print(f"  - Order {order.order_id} (status={order.status}): {order.customer_name}")

