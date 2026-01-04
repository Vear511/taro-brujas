from django.db import models
from usuarios.models import Usuario

class Tarotista(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tarotista'
    )
    descripcion = models.TextField(help_text="Bio profesional")
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Tarotista: {self.usuario.get_full_name()}"
