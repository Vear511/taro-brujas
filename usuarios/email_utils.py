import sys
import traceback
import requests

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def _send_email_via_sendgrid(to_email: str, subject: str, plain_text: str) -> bool:
    """
    Envía correo vía SendGrid Web API v3.
    Requiere:
      - settings.SENDGRID_API_KEY
      - settings.SENDGRID_FROM_EMAIL (debe estar verificado en SendGrid)
    """
    api_key = getattr(settings, "SENDGRID_API_KEY", "").strip()
    from_email = getattr(settings, "SENDGRID_FROM_EMAIL", "").strip()

    if not api_key:
        print("[MAIL][SENDGRID] ERROR: SENDGRID_API_KEY no configurada", flush=True)
        return False

    if not from_email:
        print("[MAIL][SENDGRID] ERROR: SENDGRID_FROM_EMAIL no configurada", flush=True)
        return False

    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": "Brujitas"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": plain_text}],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if 200 <= resp.status_code < 300:
            print(f"[MAIL][SENDGRID] OK -> enviado a {to_email}", flush=True)
            return True

        print(
            f"[MAIL][SENDGRID] ERROR status={resp.status_code} body={resp.text[:500]}",
            flush=True,
        )
        return False

    except Exception as e:
        print("[MAIL][SENDGRID] EXCEPTION:", repr(e), flush=True)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        return False


def enviar_email_verificacion(usuario, request) -> bool:
    """
    Envía correo de verificación con link de activación.
    Retorna True/False según si SendGrid aceptó la solicitud.
    """
    subject = "Verifica tu correo electrónico"
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)

    activar_url = request.build_absolute_uri(
        reverse("usuarios:activar_cuenta", kwargs={"uidb64": uid, "token": token})
    )

    message = (
        f"Hola {usuario.username},\n\n"
        f"Por favor verifica tu correo haciendo clic en el siguiente enlace:\n{activar_url}\n\n"
        "Si no creaste esta cuenta, ignora este mensaje."
    )

    print("[MAIL] enviar_email_verificacion() -> SendGrid", flush=True)
    return _send_email_via_sendgrid(usuario.email, subject, message)

