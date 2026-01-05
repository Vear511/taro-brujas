"""
WSGI config for Brujitas project.

This file exposes the WSGI callable as a module-level variable named ``application``.
It is used by WSGI-compatible web servers for deployment.

See:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set default Django settings module for WSGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Brujitas.settings')

# WSGI application entry point
application = get_wsgi_application()
