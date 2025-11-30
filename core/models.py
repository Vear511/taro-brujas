from django.db import models
from usuarios.models import Usuario
from tarotistas.models import Tarotista
from citas.models import Cita
# ... otras importaciones si son necesarias ...

# --- Modelo Reporte (el que nos proporcionaste) ---
class Reporte(models.Model):
    # ... (código del modelo Reporte) ...
    # ...
    def __str__(self):
        return f"Reporte de {self.tarotista.usuario.get_full_name()} sobre {self.paciente.get_full_name()}"

# --- Modelo Disponibilidad (¡El que falta!) ---
class Disponibilidad(models.Model):
    # Asegúrate de que este modelo esté definido aquí.
    # Por ejemplo, podría tener campos como:
    tarotista = models.ForeignKey(Tarotista, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(...) # Campo para el día de la semana
    hora_inicio = models.TimeField(...)
    hora_fin = models.TimeField(...)
    
    class Meta:
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'

    def __str__(self):
        return f"Disponibilidad de {self.tarotista} para el día {self.dia_semana}"
