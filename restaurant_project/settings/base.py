import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)

# Parse ALLOWED_HOSTS from environment variable
_allowed_hosts_str = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,testserver')
ALLOWED_HOSTS = [s.strip() for s in _allowed_hosts_str.split(',')]

# Add platform-specific hosts (Railway, Render, etc.)
# Railway sets RAILWAY_PUBLIC_DOMAIN environment variable
_railway_domain = config('RAILWAY_PUBLIC_DOMAIN', default=None)
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# Support for custom domain via environment variable
_custom_domain = config('CUSTOM_DOMAIN', default=None)
if _custom_domain and _custom_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_custom_domain)

# If running on Railway (detect by checking for Railway environment vars)
# Add a permissive pattern for Railway domains since domain names are dynamic
_is_railway = 'RAILWAY' in os.environ or 'railway' in os.environ.get('PATH', '').lower()
if _is_railway:
    # Add all possible Railway domains that might be generated
    # Railway domains follow the pattern: web-production-XXXX.up.railway.app
    import socket
    try:
        _hostname = socket.gethostname()
        if _hostname and _hostname not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_hostname)
    except:
        pass
    
    # Also add localhost for Railway's internal communication
    if 'localhost' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('localhost')
    if '127.0.0.1' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('127.0.0.1')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'restaurant',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'restaurant.middleware.DatabaseHealthMiddleware',  # Add early to catch DB errors
    'django.contrib.sessions.middleware.SessionMiddleware',
    'restaurant.middleware.TimezoneMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'restaurant.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restaurant_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'restaurant/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Temporarily disabled custom context processors to debug issue
                # 'accounts.context_processors.user_permissions',
                # 'restaurant.context_processors.add_valid_table_id',
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurant_project.wsgi.application'

# Database - Supabase PostgreSQL with improved connection handling and fallback
import ssl

# Get database configuration from environment
_db_host = config('DB_HOST', default='')
_db_port = config('DB_PORT', default='5432', cast=int)
_db_name = config('DB_NAME', default='postgres')
_db_user = config('DB_USER', default='postgres')
_db_password = config('DB_PASSWORD', default='')

# Derive pooler and direct hosts for Supabase
# Prefer pooler host by default when possible, keep direct as fallback
_direct_host = _db_host
_pooler_host = _db_host
if _db_host and 'supabase.co' in _db_host:
    if 'pooler' in _db_host:
        # DB_HOST already points to pooler
        _pooler_host = _db_host
        _direct_host = _db_host.replace('.pooler.supabase.co', '.supabase.co') if '.pooler.supabase.co' in _db_host else _db_host
    else:
        # DB_HOST is direct: construct the pooler variant and prefer it
        _direct_host = _db_host
        # e.g. db.xyz.supabase.co -> db.xyz.pooler.supabase.co
        _pooler_host = _db_host.replace('.supabase.co', '.pooler.supabase.co')

# Database selection: enable Supabase/external Postgres when configured
# Priority: explicit USE_SUPABASE env var -> DB_HOST presence -> default False
_use_supabase_env = config('USE_SUPABASE', default=None)
_db_host_env = config('DB_HOST', default='')

if _use_supabase_env is None:
    # Auto-enable if DB_HOST is set
    USE_SUPABASE = bool(_db_host_env)
else:
    USE_SUPABASE = config('USE_SUPABASE', default=False, cast=bool)

if USE_SUPABASE:
    # Resolve DB host and attempt fallback from pooler -> direct if DNS fails
    import socket

    _configured_db_host = config('DB_HOST', default='')
    _db_host_to_use = _configured_db_host

    def _resolves(hostname):
        try:
            socket.getaddrinfo(hostname, None)
            return True
        except Exception:
            return False

    if _configured_db_host:
        if not _resolves(_configured_db_host):
            # Try pooler -> direct fallback
            if '.pooler.supabase.co' in _configured_db_host:
                _candidate = _configured_db_host.replace('.pooler.supabase.co', '.supabase.co')
                if _resolves(_candidate):
                    _db_host_to_use = _candidate
            else:
                # If direct failed, try pooler variant
                _candidate = _configured_db_host.replace('.supabase.co', '.pooler.supabase.co')
                if _resolves(_candidate):
                    _db_host_to_use = _candidate

    # Basic external Postgres configuration (expect DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='postgres'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': _db_host_to_use,
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
            'ATOMIC_REQUESTS': False,
            'OPTIONS': {
                'connect_timeout': 10,
                'sslmode': 'require' if 'supabase' in (_db_host_to_use or '') else 'disable',
            }
        }
    }
    # Enable router only when using external DB (fallback router will route to direct if needed)
    DATABASE_ROUTERS = ['restaurant_project.db_router.PoolerFallbackRouter']
else:
    # Use local SQLite during development or when not using Supabase
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Logging configuration for database connection debugging
# Note: File logging is disabled on Render due to ephemeral filesystem
# File logs only work on local development

_logs_dir = os.path.join(BASE_DIR, 'logs')
_has_logs_dir = os.path.exists(_logs_dir)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Add file handler only if logs directory exists (local development)
if _has_logs_dir and DEBUG:
    LOGGING['handlers']['file'] = {
        'class': 'logging.FileHandler',
        'filename': os.path.join(_logs_dir, 'django.log'),
        'formatter': 'verbose',
        'level': 'DEBUG',
    }
    LOGGING['loggers']['django']['handlers'].append('file')
    LOGGING['loggers']['django.db.backends']['handlers'].append('file')

# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = 'login'

# Database router for pooler fallback handling
DATABASE_ROUTERS = ['restaurant_project.db_router.PoolerFallbackRouter']

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Use custom user model from accounts app
AUTH_USER_MODEL = 'accounts.User'

# Production Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


