from django.utils import timezone
from django.conf import settings
from zoneinfo import ZoneInfo


class TimezoneMiddleware:
    """Activate timezone per request based on a cookie or authenticated user preference.

    Priority: user.profile timezone (if present) > cookie `user_timezone` > default
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = None

        # If authenticated user has a timezone attribute (optional), prefer it
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            tzname = getattr(user, 'timezone', None)

        # Fallback to cookie set by client-side JS
        if not tzname:
            tzname = request.COOKIES.get('user_timezone')

        if tzname:
            try:
                timezone.activate(ZoneInfo(tzname))
            except Exception:
                # invalid tzname -> fall back to project TIME_ZONE
                try:
                    timezone.activate(ZoneInfo(settings.TIME_ZONE))
                except Exception:
                    timezone.deactivate()
        else:
            # no tz provided -> activate project default timezone
            try:
                timezone.activate(ZoneInfo(settings.TIME_ZONE))
            except Exception:
                timezone.deactivate()

        response = self.get_response(request)
        return response


class LoginRequiredMiddleware:
    """Redirect unauthenticated users to the login page for protected views.

    Behavior:
    - If the user is not authenticated and the path is not an allowed public path
      (login/logout, admin, static, media), redirect to `settings.LOGIN_URL` with
      a `next` parameter.
    - If the request is an AJAX request, return a 401 JSON response instead of redirecting.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        from django.http import JsonResponse

        path = (request.path or '').lstrip('/')

        # Allow static/media/admin and the login/logout paths
        allowed_prefixes = [
            (settings.LOGIN_URL or '').lstrip('/'),
            'accounts/login',
            'accounts/logout',
            'admin',
            (getattr(settings, 'STATIC_URL', '') or '').lstrip('/'),
            (getattr(settings, 'MEDIA_URL', '') or '').lstrip('/'),
        ]

        # Normalize empty strings
        allowed_prefixes = [p for p in allowed_prefixes if p]

        def is_allowed(p):
            for prefix in allowed_prefixes:
                if p.startswith(prefix):
                    return True
            return False

        # If not authenticated and not an allowed path, block/redirect
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            if not is_allowed(path):
                # AJAX/XHR requests should get JSON 401
                is_xhr = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('accept') or '')
                if is_xhr:
                    return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
                login_url = settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') else '/accounts/login/'
                return_url = f"{login_url}?next={request.path}"
                from django.shortcuts import redirect
                return redirect(return_url)

        return self.get_response(request)
