"""
Generate sample orders for testing ML forecasting.
Run: python manage.py shell < restaurant/ml/generate_sample_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import Order, OrderItem, MenuItem, Category, Table
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta
import random

print("=" * 80)
print("GENERATING SAMPLE DATA FOR ML FORECASTING")
print("=" * 80)

# Get or create a user
user, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
)

# Get categories and menu items
categories = Category.objects.all()
menu_items = MenuItem.objects.all()

if not categories or not menu_items:
    print("\n⚠️  WARNING: No categories or menu items found!")
    print("Please create at least one category and menu item first.")
    print("\nTo create sample data:")
    print("1. Go to /restaurant/categories/")
    print("2. Create a category (e.g., 'Main Course')")
    print("3. Go to /restaurant/menuitems/")
    print("4. Create menu items in that category")
    print("\nThen run this script again.")
    exit(1)

menu_items = list(menu_items)[:5]  # Use first 5 items

print(f"\nFound {len(categories)} categories and {len(menu_items)} menu items")
print(f"Will generate 90 days of sample orders...")

# Generate orders for the last 90 days
orders_created = 0
start_date = datetime.now() - timedelta(days=90)

for day_offset in range(90):
    # Create 2-8 orders per day randomly
    num_orders = random.randint(2, 8)
    
    for order_num in range(num_orders):
        order_date = start_date + timedelta(days=day_offset, hours=random.randint(8, 22))
        
        # Random order type
        order_type = random.choice(['delivery', 'takeaway'])
        
        # Create order
        order = Order.objects.create(
            customer_name=f"Customer {random.randint(1000, 9999)}",
            customer_phone=f"9841{random.randint(100000, 999999)}",
            order_type=order_type,
            total_amount=Decimal('0'),  # Will calculate
            delivery_charge=Decimal('50') if order_type == 'delivery' else Decimal('0'),
            delivery_address="Sample Address" if order_type == 'delivery' else None,
            created_at=order_date,
            created_by=user,
        )
        
        # Add 2-5 items to each order
        total = Decimal('0')
        num_items = random.randint(2, 5)
        for _ in range(num_items):
            item = random.choice(menu_items)
            quantity = random.randint(1, 3)
            
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=quantity,
                price=item.price,
            )
            
            total += Decimal(str(item.price)) * quantity
        
        # Update order total
        order.total_amount = total
        order.save()
        
        orders_created += 1

print(f"\n✅ Created {orders_created} sample orders across 90 days")
print(f"   Date range: {start_date.date()} to {datetime.now().date()}")

# Show summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_revenue = Order.objects.aggregate(total=django.db.models.Sum('total_amount'))['total'] or 0
total_orders = Order.objects.count()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

print(f"\nTotal Orders: {total_orders}")
print(f"Total Revenue: Rs.{float(total_revenue):.2f}")
print(f"Average Order Value: Rs.{float(avg_order_value):.2f}")
print(f"Daily Average: {total_orders / 90:.1f} orders/day")
print(f"Revenue/Day: Rs.{float(total_revenue) / 90:.2f}/day")

print("\n" + "=" * 80)
print("✅ SAMPLE DATA READY FOR FORECASTING!")
print("=" * 80)
print("\nYou can now:")
print("1. Access the forecasting dashboard: /restaurant/ml/forecast/")
print("2. Or test via Python:")
print("")
print("   from restaurant.ml import get_order_timeseries, ARIMAForecast")
print("   ts = get_order_timeseries()")
print("   model = ARIMAForecast()")
print("   model.fit(ts)")
print("   forecast = model.forecast(periods=30)")
print("")
