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
                return redirect('accounts:login')

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


def require_module_access(module_name):
    """Decorator to require access to a specific module
    
    Usage:
        @require_module_access('kitchen')
        def kitchen_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            # Check if user is authenticated
            if not user or not user.is_authenticated:
                return redirect('accounts:login')
            
            # Superusers always have access
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if staff has module access
            try:
                staff = user.staff_profile
                if module_name == 'dashboard':
                    # Dashboard requires ALL permissions
                    if staff.has_all_permissions():
                        return view_func(request, *args, **kwargs)
                else:
                    # Other modules require just that module permission
                    if staff.has_module_access(module_name):
                        return view_func(request, *args, **kwargs)
            except Staff.DoesNotExist:
                pass
            
            # Access denied
            error_msg = 'Dashboard requires all module permissions' if module_name == 'dashboard' else f'Access to {module_name} module denied'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_msg}, status=403)
            return HttpResponseForbidden(error_msg)
        
        return _wrapped
    return decorator
