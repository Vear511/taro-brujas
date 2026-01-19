import sys
import os
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

    # Versión de texto plano (respaldo)
    plain_text_message = (
        f"Hola {usuario.username},\n\n"
        f"Por favor verifica tu correo haciendo clic en el siguiente enlace:\n{activar_url}\n\n"
        "Si no creaste esta cuenta, ignora este mensaje."
    )

    # Versión HTML estética con botón
    html_message = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verifica tu correo</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
                text-align: center;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #d4af37 0%, #b8860b 100%);
                color: #fff;
                padding: 20px;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 30px 20px;
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #d4af37;
                color: #000 !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                margin: 20px 0;
                transition: background-color 0.3s ease;
            }}
            .button:hover {{
                background-color: #b8860b;
            }}
            .footer {{
                background-color: #f9f9f9;
                padding: 15px;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #eee;
            }}
            @media (max-width: 600px) {{
                .container {{
                    margin: 10px;
                }}
                .content {{
                    padding: 20px 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                ✨ Verifica tu correo electrónico ✨
            </div>
            <div class="content">
                <p>Hola <strong>{usuario.username}</strong>,</p>
                <p>Gracias por registrarte. Para activar tu cuenta y comenzar a disfrutar de nuestros servicios místicos, confirma tu correo haciendo clic en el botón a continuación:</p>
                <a href="{activar_url}" class="button">Confirmar correo</a>
                <p style="font-size: 14px; color: #777;">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                    <a href="{activar_url}" style="color: #d4af37; word-break: break-all;">{activar_url}</a>
                </p>
                <p style="font-size: 14px; color: #777;">
                    Si no solicitaste esta verificación, ignora este mensaje.
                </p>
            </div>
            <div class="footer">
                <p>Este es un correo automático. No respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Verificaciones: Asegura que el contenido no esté vacío
    html_message = html_message.strip()
    plain_text_message = plain_text_message.strip()
    if not html_message or not plain_text_message:
        print("[MAIL] ERROR: El mensaje (HTML o texto) está vacío", flush=True)
        return False

    # Debug: Imprime parte del HTML para verificar
    print(f"[MAIL] HTML generado (primeros 200 chars): {html_message[:200]}...", flush=True)
    print("[MAIL] enviar_email_verificacion() -> SendGrid (HTML estético con botón)", flush=True)
    return _send_email_via_sendgrid(usuario.email, subject, plain_text_message, html_message)
