from .models import Table

def add_valid_table_id(request):
    valid_table_id = Table.objects.first().id if Table.objects.exists() else None
    return {'valid_table_id': valid_table_id}