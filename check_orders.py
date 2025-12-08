from restaurant.models import Order

orders = Order.objects.all().order_by('created_at')
print(f'Total: {orders.count()}')
print(f'\nFirst 10 orders:')
for i, o in enumerate(orders[:10]):
    print(f'{i}: {o.created_at} -> date {o.created_at.date()}')

dates = set(o.created_at.date() for o in orders)
print(f'\nUnique dates: {len(dates)}')
if len(dates) > 1:
    sorted_dates = sorted(dates)
    print(f'Date range: {sorted_dates[0]} to {sorted_dates[-1]}')
else:
    print(f'All orders on same date: {list(dates)[0]}')
    if settled > 0:
        print(f"  Order {order.order_id} ({order.id}): Rs.{settled}, warning shown")
