"""
Generate dummy orders distributed over a past interval.

Usage:
  python manage.py generate_dummy_orders --count 120 --months 9

This command will create `count` orders evenly distributed over the last `months` months.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random
from django.db import connection

from restaurant.models import Order, OrderItem, MenuItem, Category, Table
from accounts.models import User


class Command(BaseCommand):
    help = 'Generate dummy orders (count) evenly distributed over last (months) months'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=120, help='Number of orders to create')
        parser.add_argument('--months', type=int, default=9, help='Number of months in the past to distribute orders')

    def handle(self, *args, **options):
        count = options.get('count', 120)
        months = options.get('months', 9)

        now = timezone.now()
        # Approximate 1 month = 30 days for distribution
        total_days = max(1, months * 30)
        start_date = now - timedelta(days=total_days)

        # Load necessary objects
        menu_items = list(MenuItem.objects.filter(is_available=True))
        tables = list(Table.objects.all())
        user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})

        if not menu_items:
            self.stdout.write(self.style.ERROR('No available MenuItem found. Create menu items first.'))
            return

        self.stdout.write(f'Generating {count} orders distributed from {start_date.date()} to {now.date()}...')

        orders_with_dates = []

        # Even spacing in days between orders
        if count > 1:
            step_days = total_days / (count - 1)
        else:
            step_days = 0

        for i in range(count):
            # Evenly spaced day, plus random seconds within the day
            offset = int(round(i * step_days))
            order_date = start_date + timedelta(days=offset)
            # randomize time within day
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            order_datetime = order_date.replace(hour=hour, minute=minute, second=second)

            # randomize order type
            order_type = random.choices(['delivery', 'takeaway', 'table'], weights=[40, 30, 30], k=1)[0]

            order = Order(
                customer_name=f'Dummy {random.randint(1000,9999)}',
                customer_phone=f'9841{random.randint(100000,999999)}',
                order_type=order_type,
                total_amount=Decimal('0'),
                delivery_charge=Decimal(random.choice([0, 50, 75, 100])) if order_type == 'delivery' else Decimal('0'),
                delivery_address='Auto-generated' if order_type == 'delivery' else None,
                table=random.choice(tables) if (tables and order_type == 'table') else None,
                created_by=user,
            )

            # add 1-4 items
            num_items = random.randint(1, 4)
            items = []
            total = Decimal('0')
            for _ in range(num_items):
                item = random.choice(menu_items)
                qty = random.randint(1, 3)
                items.append({'item': item, 'quantity': qty, 'price': item.price})
                total += Decimal(str(item.price)) * qty

            order.total_amount = total
            orders_with_dates.append({'order': order, 'created_at': order_datetime, 'items': items})

        # Bulk create orders
        orders_to_create = [o['order'] for o in orders_with_dates]
        created_orders = Order.objects.bulk_create(orders_to_create, batch_size=100)

        # Update created_at for each created order via direct SQL
        with connection.cursor() as cursor:
            for idx, ord_obj in enumerate(created_orders):
                desired = orders_with_dates[idx]['created_at']
                cursor.execute('UPDATE restaurant_order SET created_at = %s WHERE id = %s', [desired, ord_obj.id])

        # Create OrderItem records
        order_items = []
        for idx, ord_obj in enumerate(created_orders):
            for it in orders_with_dates[idx]['items']:
                order_items.append(OrderItem(order=ord_obj, item=it['item'], quantity=it['quantity'], price=it['price']))

        OrderItem.objects.bulk_create(order_items, batch_size=200)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_orders)} orders and {len(order_items)} order items'))
