from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Usuario custom del sistema.
    - avatar: foto de perfil (ImageField) -> con Cloudinary se almacena remoto automáticamente.
    - es_tarotista: para diferenciar roles.
    - email_verificado: para flujos de verificación.
    """

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    es_tarotista = models.BooleanField(default=False)
    email_verificado = models.BooleanField(default=False)

    def __str__(self):
        return self.username
