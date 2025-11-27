from django.db import models
from usuarios.models import Usuario
from tarotistas.models import Tarotista
from citas.models import Cita

class Reporte(models.Model):
    ESTADOS = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
    ]
    
    tarotista = models.ForeignKey(Tarotista, on_delete=models.CASCADE, related_name='reportes')
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes_paciente')
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes')
    experiencia = models.TextField(help_text="Experiencia con el paciente y detalles de la consulta")
    estado = models.CharField(max_length=10, choices=ESTADOS, default='abierto')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_reporte']
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
    
    def __str__(self):
        return f"Reporte de {self.tarotista.usuario.get_full_name()} sobre {self.paciente.get_full_name()}"
