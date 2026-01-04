from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

def enviar_email_verificacion(usuario, request):
    subject = 'Verifica tu correo electrónico'
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    url = request.build_absolute_uri(
        reverse('usuarios:activar_cuenta', kwargs={'uidb64': uid, 'token': token})
    )
    message = f'Hola {usuario.username},\n\nPor favor verifica tu correo haciendo clic en el siguiente enlace:\n{url}\n\nSi no creaste esta cuenta, ignora este mensaje.'
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [usuario.email])
    except Exception as e:
        import logging
        logging.error(f"Error enviando correo de verificación: {e}")
        print(f"Error enviando correo de verificación: {e}")
