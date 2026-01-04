import sys
import traceback

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def enviar_email_verificacion(usuario, request):
    print("[MAIL] entrar enviar_email_verificacion()", flush=True)

    subject = "Verifica tu correo electrónico"
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)

    url = request.build_absolute_uri(
        reverse("usuarios:activar_cuenta", kwargs={"uidb64": uid, "token": token})
    )
    message = (
        f"Hola {usuario.username},\n\n"
        f"Verifica tu correo haciendo clic:\n{url}\n\n"
        "Si no creaste esta cuenta, ignora este mensaje."
    )

    print(f"[MAIL] from={settings.DEFAULT_FROM_EMAIL} to={usuario.email}", flush=True)
    print("[MAIL] llamando send_mail()", flush=True)

    try:
        res = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=False,
        )
        print(f"[MAIL] send_mail() retornó: {res}", flush=True)
    except Exception as e:
        print("[MAIL] ERROR en send_mail():", repr(e), flush=True)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()

