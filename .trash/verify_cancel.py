import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import OrderHistory

cancelled = OrderHistory.objects.filter(status='cancelled')
print(f'Total cancelled orders: {cancelled.count()}')
for oh in cancelled:
    print(f'  - Order {oh.order_id} (pk={oh.pk}): {oh.cancellation_reason}')
