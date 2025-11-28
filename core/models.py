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

# tarotistas/models.py

from django.db import models
# Importamos el modelo de Usuario (asumiendo que está en la app 'usuarios')
from usuarios.models import Usuario 


# En tu app de tarotistas (ej. tarotistas/signals.py)

from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Usuario
from .models import Tarotista # Importa tu modelo Tarotista

# Decorador que conecta esta función a la señal
@receiver(post_save, sender=Usuario)
def crear_perfil_tarotista(sender, instance, created, **kwargs):
    """
    Función que se ejecuta CADA VEZ que se guarda un objeto Usuario.
    Si el usuario es nuevo ('created' es True), crea un perfil de Tarotista.
    """
    if created:
        # Asegúrate de que solo se cree si es un tipo de usuario 'tarotista' si tienes un campo de rol.
        # Si no tienes un campo de rol, se creará para TODOS los usuarios.
        
        # Ejemplo si Usuario tiene un campo 'rol' (ej. rol='TAROTISTA'):
        # if instance.rol == 'TAROTISTA':
        
        try:
            Tarotista.objects.create(usuario=instance)
            print(f"DEBUG: Perfil de Tarotista creado automáticamente para {instance.username}")
        except Exception as e:
             # Esto debería evitar que el sistema falle si ya existe un perfil por alguna razón
            print(f"ADVERTENCIA: No se pudo crear el perfil de Tarotista para {instance.username}. Error: {e}")

# Opcional: Para guardar el perfil si se edita el usuario
@receiver(post_save, sender=Usuario)
def guardar_perfil_tarotista(sender, instance, **kwargs):
    # Esto es útil si tienes campos en Tarotista que quieres sincronizar
    if hasattr(instance, 'tarotista'):
        instance.tarotista.save()
