from django.db import models
from usuarios.models import Usuario  # ← Importar después de que Usuario exista

class Tarotista(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='tarotista')
    especialidad = models.CharField(max_length=100)
    experiencia = models.IntegerField(help_text="Años de experiencia")
    precio_por_sesion = models.DecimalField(max_digits=6, decimal_places=2)
    descripcion = models.TextField(help_text="Bio profesional")
    disponible = models.BooleanField(default=True)
    calificacion = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Tarotista: {self.usuario.get_full_name()}"