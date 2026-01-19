import sys
import traceback
import requests

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def _send_email_via_sendgrid(to_email: str, subject: str, plain_text: str = None, html_text: str = None) -> bool:
    """
    Envía correo vía SendGrid Web API v3.
    Requiere:
      - settings.SENDGRID_API_KEY
      - settings.SENDGRID_FROM_EMAIL (debe estar verificado en SendGrid)
    Ahora soporta HTML para emails más estéticos.
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

    # Construye el contenido: Incluye texto plano y/o HTML si están disponibles
    content = []
    if plain_text and plain_text.strip():
        content.append({"type": "text/plain", "value": plain_text.strip()})
    if html_text and html_text.strip():
        content.append({"type": "text/html", "value": html_text.strip()})

    if not content:
        print("[MAIL][SENDGRID] ERROR: No hay contenido válido para enviar", flush=True)
        return False

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
    """
    Envía correo de verificación con link de activación.
    Retorna True/False según si SendGrid aceptó la solicitud.
    Ahora usa HTML para un diseño estético con botón.
    """
    subject = "Verifica tu correo electrónico"
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)

    activar_url = request.build_absolute_uri(
        reverse("usuarios:activar_cuenta", kwargs={"uidb64": uid, "token": token})
    )

    # Mensaje de texto plano (respaldo para clientes que no soportan HTML)
    plain_text = (
        f"Hola {usuario.username},\n\n"
        f"Por favor verifica tu correo haciendo clic en el siguiente enlace:\n{activar_url}\n\n"
        "Si no creaste esta cuenta, ignora este mensaje."
    )

    # Mensaje HTML estético con botón
    html_text = f"""
    <html>
      <body style="font-family: Arial, Helvetica, sans-serif; color: #222; margin: 0; padding: 20px; background-color: #f9f9f9;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
          <h2 style="color: #333; text-align: center;">Verifica tu correo electrónico</h2>
          <p>Hola <strong>{usuario.username}</strong>,</p>
          <p>Por favor confirma tu correo haciendo clic en el botón a continuación:</p>
          <div style="text-align: center; margin: 20px 0;">
            <a href="{activar_url}" style="
                display: inline-block;
                padding: 12px 24px;
                background-color: #ffc107;
                color: #000;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #ffc107;
                transition: background-color 0.3s;
            ">Confirmar correo</a>
          </div>
          <p style="font-size: 14px; color: #666; text-align: center;">
            Si no solicitaste esta acción, puedes ignorar este correo.
          </p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #999; text-align: center;">
            Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
            <a href="{activar_url}" style="color: #007bff; word-break: break-all;">{activar_url}</a>
          </p>
        </div>
      </body>
    </html>
    """

    print("[MAIL] enviar_email_verificacion() -> SendGrid (con HTML estético)", flush=True)
    return _send_email_via_sendgrid(usuario.email, subject, plain_text, html_text)


