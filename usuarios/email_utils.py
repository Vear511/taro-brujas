import threading
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)


def enviar_email_verificacion(usuario, request):
    subject = "Verifica tu correo electrónico"
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)

    url = request.build_absolute_uri(
        reverse("usuarios:activar_cuenta", kwargs={"uidb64": uid, "token": token})
    )

    message = (
        f"Hola {usuario.username},\n\n"
        f"Por favor verifica tu correo haciendo clic en el siguiente enlace:\n{url}\n\n"
        "Si no creaste esta cuenta, ignora este mensaje."
    )

    from_email = settings.DEFAULT_FROM_EMAIL
    to_emails = [usuario.email]

    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=to_emails,
                fail_silently=False,
            )
            logger.info("Correo de verificación enviado a %s", usuario.email)
        except Exception:
            # Importantísimo: deja evidencia pero no tumba la app
            logger.exception("Error enviando correo de verificación a %s", usuario.email)

    # Enviar sin bloquear el request
    threading.Thread(target=_send, daemon=True).start()
