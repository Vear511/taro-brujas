from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class BloqueadoBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and user.bloqueado:
            raise ValidationError('Tu cuenta ha sido bloqueada. Contacta al administrador.')
        return user
