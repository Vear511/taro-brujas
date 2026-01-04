"""
Django settings for Brujitas project.
Local + producción (Railway).

Incluye:
- DB: DATABASE_URL (Railway) o SQLite (local)
- Static: WhiteNoise (collectstatic)
- Email: SendGrid API como EMAIL_BACKEND global (sirve para reset password también)
- Media: Cloudinary si existe CLOUDINARY_URL, si no carpeta /media (local)
"""

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# ENV / DEBUG
# --------------------------------------------------
DEBUG = os.getenv("DEBUG", "0") == "1"

# Solo cargar .env en local (DEBUG=1)
if DEBUG:
    load_dotenv()

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está definida en variables de entorno")

RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()

# Si quieres controlar esto por variable:
# ALLOWED_HOSTS=".railway.app,localhost,127.0.0.1,taro-brujas-production.up.railway.app"
raw_hosts = os.getenv("ALLOWED_HOSTS", "").strip()
if raw_hosts:
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]
else:
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
            ],
        },
    },
]

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

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
# I18N / TZ
# --------------------------------------------------
LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

_static_dir = BASE_DIR / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------------------------------
# MEDIA (Cloudinary en producción)
# --------------------------------------------------
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "").strip()

if CLOUDINARY_URL:
    # Se habilita Cloudinary si existe variable en Railway
    INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

    # Django exige definir MEDIA_URL, aunque Cloudinary entregue URLs completas
    MEDIA_URL = "/media/"
else:
    # Local / sin Cloudinary (ojo: en Railway NO recomendado)
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# CSRF / SECURITY (PROD)
# --------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
]

if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --------------------------------------------------
# EMAIL (GLOBAL via SendGrid API)
# --------------------------------------------------
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "").strip() or "brujitas.uoh@gmail.com"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", SENDGRID_FROM_EMAIL)

EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "20"))

# Esto hace que *cualquier* send_mail() (reset password, confirmaciones, etc.) use SendGrid API
EMAIL_BACKEND = "usuarios.email_backend.SendGridEmailBackend"

# --------------------------------------------------
# DEFAULT
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
