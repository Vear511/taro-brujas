from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Usuario custom del sistema.

    Campos históricos usados en el proyecto (templates/views/admin):
    - rut, telefono, fecha_nacimiento, apodo, bio
    - bloqueado, creado_en

    Campos actuales:
    - avatar
    - es_tarotista
    - email_verificado
    """

    rut = models.CharField("RUT", max_length=12, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    apodo = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    bloqueado = models.BooleanField(default=False, help_text="Impide que el usuario inicie sesión")
    creado_en = models.DateTimeField(auto_now_add=True)

    es_tarotista = models.BooleanField(default=False)
    email_verificado = models.BooleanField(default=False)

    def __str__(self):
        return self.username
