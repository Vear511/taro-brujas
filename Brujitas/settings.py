from pathlib import Path
import os
import dj_database_url

# Asegúrate de que dj_database_url esté instalado: pip install dj-database-url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# CONFIGURACIÓN GENERAL
# -------------------------

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-clave-temporal')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

if DEBUG:
    # Base de datos local (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Base de datos en Railway (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv("DATABASE_URL", ""),  # mejor usar variable de entorno
            conn_max_age=600,
            ssl_require=True
        )
    }



# Ajusta el host de Railway para evitar problemas en producción
ALLOWED_HOSTS = ['.railway.app', 'localhost', '127.0.0.1']


# -------------------------
# APPS
# -------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tus Apps
    'usuarios',
    'citas',
    'tarotistas',
    'core',
]

# -------------------------
# MIDDLEWARE (Duplicidades eliminadas)
# -------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'Brujitas.urls'

# -------------------------
# TEMPLATES
# -------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Brujitas.wsgi.application'

# -------------------------
# BASE DE DATOS (Hardcodeada para diagnóstico - ¡TEMPORAL!)
# -------------------------

# WARNING: ESTA URL CONTIENE CREDENCIALES Y DEBE ELIMINARSE DESPUÉS DE LA PRUEBA.
DATABASE_URL_HARDCODED = 'postgresql://postgres:PXVoBhORsOECYeHxrwIbcELwJAsPmpor@hopper.proxy.rlwy.net:22112/railway'


# -------------------------
# VALIDADORES DE CONTRASEÑA
# -------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------
# LOCALIZACIÓN
# -------------------------

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------
# ARCHIVOS ESTÁTICOS (STATICFILES)
# -------------------------

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Archivos recolectados para producción
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Origen de tus archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # Para Whitenoise

# -------------------------
# MEDIA
# -------------------------

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------
# USUARIO PERSONALIZADO Y AUTENTICACIÓN
# -------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'usuarios.Usuario'

# Configuración que causa el error, pero es necesaria para el BloqueoBackend.
# El error se soluciona en la vista 'registro' especificando el backend.
AUTHENTICATION_BACKENDS = [
    'usuarios.backends.BloqueadoBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# -------------------------
# LOGGING
# -------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# -------------------------
# CSRF PARA RAILWAY
# -------------------------

CSRF_TRUSTED_ORIGINS = [
    'https://brujitas-production.up.railway.app',
    'https://*.railway.app',
]
