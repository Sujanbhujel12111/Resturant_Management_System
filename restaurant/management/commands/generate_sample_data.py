"""
Django management command to generate sample data for testing.
Usage: python manage.py generate_sample_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from restaurant.models import Order, OrderItem, MenuItem, Category, Table
from accounts.models import User
from decimal import Decimal
from datetime import datetime, timedelta
import random
import logging
from pytz import UTC

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate sample orders for testing ML forecasting'

    def handle(self, *args, **options):
        print("\n" + "=" * 80)
        print("GENERATING SAMPLE DATA FOR ML FORECASTING")
        print("=" * 80)

        # Get or create a user
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )

        # Get categories and menu items
        categories = list(Category.objects.all())
        menu_items = list(MenuItem.objects.all())

        if not categories or not menu_items:
            self.stdout.write(self.style.ERROR(
                '\nWARNING: No categories or menu items found!'
            ))
            self.stdout.write('Please create at least one category and menu item first.\n')
            self.stdout.write('To create sample data:')
            self.stdout.write('1. Go to /restaurant/categories/')
            self.stdout.write('2. Create a category (e.g., "Main Course")')
            self.stdout.write('3. Go to /restaurant/menuitems/')
            self.stdout.write('4. Create menu items in that category')
            self.stdout.write('\nThen run: python manage.py generate_sample_data\n')
            return

        menu_items = menu_items[:5]  # Use first 5 items

        self.stdout.write(f'\nFound {len(categories)} categories and {len(menu_items)} menu items')
        self.stdout.write('Will generate 90 days of sample orders...\n')

        # Generate orders for the last 90 days
        orders_created = 0
        # Get current UTC date time and work backwards
        now_utc = timezone.now()
        
        # Store all orders with their desired dates
        orders_with_dates = []
        all_items = []
        
        for days_ago in range(90):
            # Create 2-8 orders per day randomly
            num_orders = random.randint(2, 8)
            order_date_base = now_utc - timedelta(days=days_ago)
            
            for order_num in range(num_orders):
                # Create order with different time of day
                hour = random.randint(8, 22)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                # Create a timezone-aware datetime by replacing the time
                order_datetime = order_date_base.replace(hour=hour, minute=minute, second=second)
                
                # Random order type
                order_type = random.choice(['delivery', 'takeaway'])
                
                # Create order instance
                order = Order(
                    customer_name=f"Customer {random.randint(1000, 9999)}",
                    customer_phone=f"9841{random.randint(100000, 999999)}",
                    order_type=order_type,
                    total_amount=Decimal('0'),  # Will calculate
                    delivery_charge=Decimal('50') if order_type == 'delivery' else Decimal('0'),
                    delivery_address="Sample Address" if order_type == 'delivery' else None,
                    created_by=user,
                )
                
                # Add 2-5 items to each order
                total = Decimal('0')
                num_items = random.randint(2, 5)
                items_for_order = []
                for _ in range(num_items):
                    item = random.choice(menu_items)
                    quantity = random.randint(1, 3)
                    items_for_order.append({
                        'item': item,
                        'quantity': quantity,
                        'price': item.price,
                    })
                    total += Decimal(str(item.price)) * quantity
                
                # Update order total
                order.total_amount = total
                
                # Store order with its desired date and items
                orders_with_dates.append({
                    'order': order,
                    'created_at': order_datetime,
                    'items': items_for_order,
                })
        
        # Create orders (they'll get today's date due to auto_now_add)
        orders_to_create = [o['order'] for o in orders_with_dates]
        created_orders = Order.objects.bulk_create(orders_to_create, batch_size=100)
        
        # Immediately update their created_at using raw SQL (bypasses auto_now_add)
        from django.db import connection
        with connection.cursor() as cursor:
            for i, order in enumerate(created_orders):
                desired_date = orders_with_dates[i]['created_at']
                cursor.execute(
                    f"UPDATE restaurant_order SET created_at = %s WHERE id = %s",
                    [desired_date, order.id]
                )
        
        # Create order items
        order_items_to_create = []
        for i, order in enumerate(created_orders):
            for item_info in orders_with_dates[i]['items']:
                order_item = OrderItem(
                    order=order,
                    item=item_info['item'],
                    quantity=item_info['quantity'],
                    price=item_info['price'],
                )
                order_items_to_create.append(order_item)
        
        OrderItem.objects.bulk_create(order_items_to_create, batch_size=100)
        orders_created = len(created_orders)
        
        start_date = now_utc - timedelta(days=89)
        self.stdout.write(self.style.SUCCESS(f'\nCreated {orders_created} sample orders across 90 days'))
        self.stdout.write(f'Date range: {start_date.date()} to {now_utc.date()}')

        # Show summary
        from django.db.models import Sum
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = Order.objects.count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        self.stdout.write(f'\nTotal Orders: {total_orders}')
        self.stdout.write(f'Total Revenue: Rs.{float(total_revenue):.2f}')
        self.stdout.write(f'Average Order Value: Rs.{float(avg_order_value):.2f}')
        self.stdout.write(f'Daily Average: {total_orders / 90:.1f} orders/day')
        self.stdout.write(f'Revenue/Day: Rs.{float(total_revenue) / 90:.2f}/day')

        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        self.stdout.write(self.style.SUCCESS('\nYou can now:'))
        self.stdout.write('1. Access the forecasting dashboard: /restaurant/ml/forecast/')
        self.stdout.write('2. Or test via command line: python manage.py shell')
        self.stdout.write('   >>> from restaurant.ml import get_order_timeseries, ARIMAForecast')
        self.stdout.write('   >>> ts = get_order_timeseries()')
        self.stdout.write('   >>> model = ARIMAForecast()')
        self.stdout.write('   >>> model.fit(ts)')
        self.stdout.write('   >>> forecast = model.forecast(periods=30)\n')
