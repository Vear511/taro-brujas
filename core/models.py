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
# En tu app de tarotistas (ej. tarotistas/models.py)

from django.db import models
from usuarios.models import Usuario # Importamos tu modelo de usuario personalizado

class Tarotista(models.Model):
    # La clave que conecta a la tabla de Usuarios (usuarios_usuario)
    # primary_key=True es común para perfiles OneToOneField.
    usuario = models.OneToOneField(
        Usuario,  
        on_delete=models.CASCADE,
        related_name='tarotista' # Nombre de la relación inversa (request.user.tarotista)
    )
    
    bio = models.TextField(blank=True, null=True, default="Tarotista en formación.")
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name()}"
