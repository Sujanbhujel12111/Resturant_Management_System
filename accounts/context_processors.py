from django.conf import settings


def user_permissions(request):
    """Expose simple group and permission flags for the current user to templates.

    Returns a dict under the `user_perms` key. Example usage in templates:
      {% if user_perms.is_kitchen %} ... {% endif %}
      {% if user_perms.can_change_order %} ... {% endif %}
    """
    user = getattr(request, "user", None)
    perms = {}
    if not user or not user.is_authenticated:
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

    return {"user_perms": perms}
