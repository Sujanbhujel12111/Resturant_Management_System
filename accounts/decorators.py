from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from .models import Staff


def staff_permission_required(name):
    """Decorator that accepts either:
      - a Django permission string ("app_label.codename")
      - a group name
      - (backwards compatibility) a Staff boolean field name

    Behavior:
      - Superusers bypass checks
      - Unauthenticated users are redirected to login
      - AJAX requests receive JSON 403
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return redirect('login')

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 1) If name looks like a permission (contains dot), use has_perm
            if isinstance(name, str) and '.' in name:
                if user.has_perm(name):
                    return view_func(request, *args, **kwargs)

            # 2) If user has the permission via Django permissions (try as codename)
            if user.has_perm(name):
                return view_func(request, *args, **kwargs)

            # 3) If a group with this name exists on the user
            if user.groups.filter(name=name).exists():
                return view_func(request, *args, **kwargs)

            # 4) Backwards-compat: check Staff boolean field (if present)
            try:
                staff = Staff.objects.get(user=user)
            except Staff.DoesNotExist:
                staff = None

            if staff and hasattr(staff, name) and bool(getattr(staff, name)):
                return view_func(request, *args, **kwargs)

            # Deny
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or getattr(request, 'is_ajax', lambda: False)():
                return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            return HttpResponseForbidden('Permission denied')

        return _wrapped

    return decorator
