from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    rut = models.CharField(
        max_length=12,  # largo típico de RUT chileno
        unique=True,    # no puede repetirse
        blank=True,     # permite dejar vacío en formularios
        null=True,      # permite NULL en la DB
        default=''      # valor por defecto para filas existentes 
    )
    telefono = models.CharField(max_length=15, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    apodo = models.CharField(max_length=50, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
    @property
    def es_tarotista(self):
        return hasattr(self, 'tarotista')
