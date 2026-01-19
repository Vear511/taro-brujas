import sys
import traceback
import requests

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def _send_email_via_sendgrid(to_email: str, subject: str, plain_text: str, html_text: str = None) -> bool:
    """
    Envía correo vía SendGrid Web API v3.
    Requiere:
      - settings.SENDGRID_API_KEY
      - settings.SENDGRID_FROM_EMAIL (debe estar verificado en SendGrid)

    Ahora soporta contenido HTML opcional para mostrar enlaces estéticos.
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

    # Siempre incluimos la versión plain text como fallback.
    content = [
        {"type": "text/plain", "value": plain_text}
    ]

    # Si se proporcionó html_text, lo añadimos (SendGrid acepta múltiples content parts)
    if html_text:
        content.append({"type": "text/html", "value": html_text})

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": "Brujitas"},
        "subject": subject,
        "content": content,
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
    subject = "Verifica tu correo electrónico"
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)

    activar_url = request.build_absolute_uri(
        reverse("usuarios:activar_cuenta", kwargs={"uidb64": uid, "token": token})
    )

    # Solo HTML con botón
    html_message = f"""
    <html>
      <body style="font-family: Arial, Helvetica, sans-serif; color: #222;">
        <p>Hola <strong>{usuario.first_name} {usuario.last_name}</strong>,</p>
        <p>Por favor confirma tu correo haciendo clic en el siguiente botón:</p>
        <p>
          <a href="{activar_url}" style="
              display:inline-block;
              padding:10px 18px;
              background:#ffc107;
              color:#000;
              text-decoration:none;
              border-radius:6px;
              font-weight:600;
            ">Confirmar correo</a>
        </p>
        <p style="font-size:0.9rem; color:#666;">
          Si no solicitaste esta acción, puedes ignorar este correo.
        </p>
      </body>
    </html>
    """

    print("[MAIL] enviar_email_verificacion() -> SendGrid (solo HTML con botón)", flush=True)
    return _send_email_via_sendgrid(usuario.email, subject, None, html_message)