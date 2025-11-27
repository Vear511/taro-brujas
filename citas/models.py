from django.db import models
from usuarios.models import Usuario
from tarotistas.models import Tarotista

class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas_cliente')
    tarotista = models.ForeignKey(Tarotista, on_delete=models.CASCADE, related_name='citas_tarotista')
    fecha_hora = models.DateTimeField()
    duracion = models.IntegerField(default=60)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cita {self.id} - {self.cliente} con {self.tarotista}"