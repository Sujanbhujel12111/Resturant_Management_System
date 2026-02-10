from django.apps import AppConfig


class RestaurantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurant'
    
    def ready(self):
        """Register signal handlers when the app starts."""
        import restaurant.signals  # noqa
