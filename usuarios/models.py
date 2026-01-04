# usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado del sistema.
    Extiende AbstractUser para agregar información adicional
    y control de bloqueo.
    """

    # --- Identificación ---
    rut = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        verbose_name='RUT'
    )

    # --- Información personal ---
    telefono = models.CharField(max_length=15, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    apodo = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    # --- Control y estado ---
    bloqueado = models.BooleanField(
        default=False,
        help_text='Impide que el usuario inicie sesión'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre = self.get_full_name()
        return nombre if nombre else self.username

    @property
    def es_tarotista(self):
        """
        Retorna True si el usuario tiene perfil de tarotista asociado.
        """
        return hasattr(self, 'tarotista')
