"""Compatibility WSGI wrapper that delegates to the real WSGI module.

Some hosting platforms (or legacy configs) may still try to import
`Restaurant_Management_System.wsgi`. This small wrapper ensures those
imports succeed and forwards to `restaurant_project.wsgi`.
"""
import os
import importlib

# Ensure Django settings module is set (matches existing project)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

# Import the real WSGI application and expose it as `application`
real_wsgi = importlib.import_module('restaurant_project.wsgi')
application = getattr(real_wsgi, 'application')
