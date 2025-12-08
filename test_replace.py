from django.utils import timezone
from datetime import timedelta

now = timezone.now()
print(f"now = {now}")

# Simulate the loop
for days_ago in range(3):
    order_date_base = now - timedelta(days=days_ago)
    print(f"days_ago={days_ago}, order_date_base={order_date_base}, date={order_date_base.date()}")
    
    # Try replacing hour
    test = order_date_base.replace(hour=10, minute=30)
    print(f"  after replace: {test}, date={test.date()}")
