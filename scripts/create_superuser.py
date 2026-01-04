import os
import sys

# Add project root to sys.path so Django settings can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ensure project settings are loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Brujitas.settings')

# Provide a temporary SECRET_KEY for script runs when .env isn't present
os.environ.setdefault('SECRET_KEY', 'dev-create-superuser-temp-key')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'Admin'
email = 'admin@example.com'
password = 'Admin1234'
rut_value = 'ADMIN-RUT-001'

if User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists.")
    sys.exit(0)

# Create superuser using manager
try:
    User.objects.create_superuser(username=username, email=email, password=password, rut=rut_value)
    print(f"Superuser '{username}' created successfully.")
except Exception as e:
    print('Failed to create superuser:', e)
    raise
