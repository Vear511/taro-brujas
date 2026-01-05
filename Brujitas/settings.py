"""
Django settings for Brujitas project.
Configurado para desarrollo local y producción en Railway.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import urllib.parse

# --------------------------------------------------
# BASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# DEBUG / ENV
# --------------------------------------------------

DEBUG = os.getenv("DEBUG", "0").strip() == "1"

# Cargar .env SOLO en local
if DEBUG:
    load_dotenv()

# --------------------------------------------------
# SEGURIDAD
# --------------------------------------------------

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está definida en variables de entorno")

RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()

# ALLOWED_HOSTS puede venir como CSV desde Railway: ".railway.app,localhost,127.0.0.1"
_allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]

# fallback seguro (por si no lo configuras)
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".railway.app"]

if RAILWAY_PUBLIC_DOMAIN and RAILWAY_PUBLIC_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# --------------------------------------------------
# APPS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "usuarios",
    "citas",
    "tarotistas",
    "core",

    "django_extensions",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# URLS / WSGI / ASGI
# --------------------------------------------------

ROOT_URLCONF = "Brujitas.urls"

WSGI_APPLICATION = "Brujitas.wsgi.application"
ASGI_APPLICATION = "Brujitas.asgi.application"

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # ✅ NUEVO: roles globales para templates
                "core.context_processors.user_roles",
            ],
        },
    },
]

# --------------------------------------------------
# BASE DE DATOS
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Si quieres logs, descomenta:
# print("RAW DATABASE_URL:", repr(DATABASE_URL))

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------
# AUTH
# --------------------------------------------------

AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --------------------------------------------------
# INTERNACIONALIZACIÓN
# --------------------------------------------------

LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC & MEDIA
# --------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# En producción, STATICFILES_DIRS puede causar warnings si no existe /static.
# Si tienes carpeta static en repo, déjalo; si no, comenta.
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# CSRF / SEGURIDAD PRODUCCIÓN
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
]

# si tu dominio público existe, agréguelo también
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --------------------------------------------------
# EMAIL (SendGrid recomendado)
# --------------------------------------------------
# Nota: tu proyecto ya está usando SendGrid (por logs).
# Aquí solo dejamos variables para DEFAULT_FROM_EMAIL, etc.

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "brujitas.uoh@gmail.com")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", DEFAULT_FROM_EMAIL)

# --------------------------------------------------
# DEFAULT
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
