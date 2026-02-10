#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import MenuItem

items = MenuItem.objects.all()
print(f"Total items: {items.count()}\n")

for tier in ['high', 'medium', 'low']:
    tier_items = items.filter(demand_tier=tier, is_available=True)
    print(f"\n{tier.upper()} DEMAND (Available & is_available=True):")
    if tier_items.exists():
        for item in tier_items:
            print(f"  - {item.name}: {item.order_count} orders")
    else:
        print(f"  (no items)")

print("\n\nAll items with their status:")
for item in items:
    print(f"  - {item.name}: tier={item.demand_tier}, available={item.is_available}, orders={item.order_count}")
