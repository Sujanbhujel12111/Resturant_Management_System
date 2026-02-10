from django.core.management.base import BaseCommand
from restaurant.models import OrderHistory


class Command(BaseCommand):
    help = 'Check for cancelled orders in history'

    def handle(self, *args, **options):
        cancelled_orders = OrderHistory.objects.filter(status='cancelled')
        self.stdout.write(f"Total cancelled orders: {cancelled_orders.count()}")
        
        for order in cancelled_orders:
            reason = order.cancellation_reason or "No reason provided"
            self.stdout.write(
                f"Order {order.order_id}: {reason} (Created: {order.created_at})"
            )
        
        if cancelled_orders.count() == 0:
            self.stdout.write(self.style.WARNING("No cancelled orders found in history"))
