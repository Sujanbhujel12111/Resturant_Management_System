from .models import Table
import logging

logger = logging.getLogger(__name__)

def add_valid_table_id(request):
    """
    Add the first valid table ID to the template context.
    Skips database queries for admin views to prevent template rendering issues.
    """
    # Skip database queries for admin views to avoid context pollution
    # that can cause "super object has no attribute 'dicts'" errors
    if request.path.startswith('/admin/'):
        return {'valid_table_id': None}
    
    try:
        valid_table_id = Table.objects.first().id if Table.objects.exists() else None
        return {'valid_table_id': valid_table_id}
    except Exception as e:
        # Log the error but don't crash - return empty context
        logger.warning(f"Error in add_valid_table_id context processor: {str(e)}")
        return {'valid_table_id': None}