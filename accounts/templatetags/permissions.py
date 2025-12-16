from django import template

register = template.Library()

@register.filter
def has_module_access(staff, module_name):
    """Check if staff has access to a specific module"""
    if not staff:
        return False
    return staff.has_module_access(module_name)
