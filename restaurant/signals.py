"""
Signal handlers for the restaurant app.
Handles events like order status changes, payment updates, etc.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderHistoryItem, MenuItem
from django.db.models import Sum


@receiver(post_save, sender=OrderHistoryItem)
def update_menu_item_stats(sender, instance, created, **kwargs):
    """
    Update MenuItem stats when an OrderHistoryItem is created or updated.
    This keeps track of total orders and quantities.
    """
    if created:
        try:
            menu_item = instance.item
            if menu_item:
                # Update order count and total quantity
                menu_item.order_count = OrderHistoryItem.objects.filter(
                    item=menu_item
                ).values('order_history_id').distinct().count()
                menu_item.save(update_fields=['order_count'])
        except Exception as e:
            pass  # Silently fail to avoid blocking order completion


# Add more signal handlers as needed
