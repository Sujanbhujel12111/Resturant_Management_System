from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

from .models import OrderHistory

@receiver(post_save, sender=OrderHistory)
def auto_cluster_after_order_history(sender, instance, created, **kwargs):
    """
    Automatically run K-Means clustering when a new order is added to history.
    This ensures menu item demand tiers are always up-to-date.
    """
    if created:
        try:
            # Run clustering silently (without verbose output)
            call_command('cluster_menu_items', verbosity=0)
            logger.info(f"Auto-clustering triggered after OrderHistory #{instance.order_id} was created")
        except Exception as e:
            logger.error(f"Error during auto-clustering after order history: {str(e)}")
            # Don't raise the error - we don't want order completion to fail due to clustering issues
