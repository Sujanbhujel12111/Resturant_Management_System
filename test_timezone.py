from django.utils import timezone
from datetime import timedelta

now = timezone.now()
print(f"Now: {now}")
print(f"Now date: {now.date()}")

test_date = now - timedelta(days=5)
print(f"Now - 5 days: {test_date}")
print(f"Now - 5 days date: {test_date.date()}")

# Test replace
test = now.replace(hour=10, minute=30)
print(f"Now with hour=10: {test}")
print(f"Now with hour=10 date: {test.date()}")

test2 = (now - timedelta(days=5)).replace(hour=10)
print(f"(Now - 5 days) with hour=10: {test2}")
print(f"(Now - 5 days) with hour=10 date: {test2.date()}")
