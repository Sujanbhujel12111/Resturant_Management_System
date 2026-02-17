import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def user_permissions(request):
    """Expose simple group and permission flags for the current user to templates.

    Returns a dict under the `user_perms` key. Example usage in templates:
      {% if user_perms.is_kitchen %} ... {% endif %}
      {% if user_perms.can_change_order %} ... {% endif %}
      
    Skips expensive permission checks for admin views to prevent template rendering issues.
    """
    user = getattr(request, "user", None)
    perms = {}
    if not user or not user.is_authenticated:
        return {"user_perms": perms}
    
    # Skip expensive permission checks for admin views to avoid context pollution
    if request.path.startswith('/admin/'):
        return {"user_perms": perms}

    group_names = ["kitchen", "orders", "menu", "place_order", "payments", "reports"]
    for g in group_names:
        perms[f"is_{g}"] = user.groups.filter(name=g).exists()

    # Common permission booleans useful for templates
    perms["can_change_order"] = user.has_perm("restaurant.change_order")
    perms["can_add_order"] = user.has_perm("restaurant.add_order")
    perms["can_view_order"] = user.has_perm("restaurant.view_order")
    # Manage menu if they can change menuitems or products
    perms["can_manage_menu"] = (
        user.has_perm("restaurant.change_menuitem") or user.has_perm("products.change_product")
    )
    
    # Add module access permissions
    try:
        staff = user.staff_profile
        modules = ['dashboard', 'orders', 'menu', 'kitchen', 'history', 'tables', 'takeaway', 'delivery']
        for module in modules:
            try:
                if module == 'dashboard':
                    # Dashboard requires ALL permissions
                    perms[f"has_{module}"] = staff.has_all_permissions()
                else:
                    # Other modules require just that module permission
                    perms[f"has_{module}"] = staff.has_module_access(module)
            except Exception as e:
                # Log the error but don't fail the context processor
                logger.warning(f"Error checking module access for user {user.username}: {str(e)}")
                perms[f"has_{module}"] = False
    except AttributeError:
        # User doesn't have staff profile
        pass
    except Exception as e:
        # Log any other unexpected errors but don't crash
        logger.warning(f"Unexpected error in user_permissions context processor: {str(e)}")

    return {"user_perms": perms}
