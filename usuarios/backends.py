# usuarios/backends.py

from django.contrib.auth.backends import ModelBackend

class BloqueadoBackend(ModelBackend):
    """
    Backend de autenticación que impide el inicio de sesión
    a usuarios marcados como bloqueados.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(
            request,
            username=username,
            password=password,
            **kwargs
        )

        if user is not None and getattr(user, 'bloqueado', False):
            return None

        return user
