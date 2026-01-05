import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache


def generar_codigo_verificacion():
    return ''.join(random.choices(string.digits, k=6))


def guardar_codigo_en_cache(email, code):
    key = f"reset_code_{email}"
    cache.set(key, code, timeout=1800)  # 30 min


def obtener_codigo_de_cache(email):
    key = f"reset_code_{email}"
    return cache.get(key)


def eliminar_codigo_de_cache(email):
    key = f"reset_code_{email}"
    cache.delete(key)


def enviar_codigo_reset(email, code) -> bool:
    subject = "Código de restablecimiento de contraseña"
    message = f"Tu código de verificación es: {code}\n\nEste código es válido por 30 minutos."
    try:
        # Usa EMAIL_BACKEND global (SendGrid API)
        sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        print(f"[MAIL][RESET] send_mail sent={sent} to={email}", flush=True)
        return sent > 0
    except Exception as e:
        print(f"[MAIL][RESET] ERROR enviando código a {email}: {e}", flush=True)
        raise
