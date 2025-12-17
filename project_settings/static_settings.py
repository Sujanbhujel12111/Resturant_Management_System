import os

# Helper: centralized static settings (moved from a misnamed top-level file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
