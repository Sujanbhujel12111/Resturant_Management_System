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

class DatabaseHealthMiddleware:
    """Handle database connection errors gracefully.
    
    Catches database connection errors and provides a user-friendly error page
    instead of a 500 error, helping with debugging connectivity issues.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            # Check if it's a database connectivity error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['could not translate host name', 'name or service not known', 
                                                         'connection refused', 'connection timeout', 
                                                         'server closed the connection']):
                return self.handle_db_error(request, e)
            raise

    def handle_db_error(self, request, exception):
        """Handle database connectivity errors"""
        from django.http import HttpResponse
        from django.conf import settings
        import traceback
        
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Database connection error on {request.path}: {str(exception)}", exc_info=True)
        
        # In production, show a user-friendly error page
        if not settings.DEBUG:
            error_page = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Service Temporarily Unavailable</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { background: white; padding: 30px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                    h1 { color: #d32f2f; }
                    p { color: #666; line-height: 1.6; }
                    .error-code { background: #f0f0f0; padding: 10px; border-left: 4px solid #d32f2f; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Service Temporarily Unavailable</h1>
                    <p>We're having trouble connecting to our database. Our team has been notified and is working to resolve this issue.</p>
                    <p>Please try again in a few moments.</p>
                    <div class="error-code">
                        <strong>Error Type:</strong> Database Connection Error<br>
                        <strong>Status:</strong> We're investigating
                    </div>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_page, status=503)
        
        # In debug mode, show detailed error info
        error_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Connection Error</title>
            <style>
                body {{ font-family: monospace; margin: 20px; background: #fff3cd; }}
                .error {{ background: white; padding: 20px; border: 2px solid #ff6b6b; border-radius: 5px; }}
                h2 {{ color: #d32f2f; }}
                pre {{ background: #f5f5f5; padding: 15px; overflow: auto; border-left: 4px solid #d32f2f; }}
                .section {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>🔴 Database Connection Error</h2>
                <div class="section">
                    <strong>Error:</strong> {str(exception)}
                </div>
                <div class="section">
                    <strong>Request Path:</strong> {request.path}
                </div>
                <div class="section">
                    <strong>How to debug:</strong>
                    <ul>
                        <li>Check if database environment variables are set on Render</li>
                        <li>Verify Supabase database is running and accessible</li>
                        <li>Run: <code>python manage.py db_health_check --verbose</code></li>
                        <li>Check Render logs for more details</li>
                    </ul>
                </div>
                <div class="section">
                    <strong>Traceback:</strong>
                    <pre>{traceback.format_exc()}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_page, status=503)