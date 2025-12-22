from django.db import models
from usuarios.models import Usuario
from tarotistas.models import Tarotista
from citas.models import Cita


# -------------------------------------------------
# Modelo Reporte
# -------------------------------------------------
class Reporte(models.Model):
    ESTADOS = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
    ]

    tarotista = models.ForeignKey(
        Tarotista,
        on_delete=models.CASCADE,
        related_name='reportes'
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reportes_paciente'
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes'
    )

    experiencia = models.TextField(
        help_text="Experiencia con el paciente y detalles de la consulta"
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='abierto'
    )

    fecha_reporte = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_reporte']
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'

    def __str__(self):
        return (
            f"Reporte de {self.tarotista.usuario.get_full_name()} "
            f"sobre {self.paciente.get_full_name()}"
        )


# -------------------------------------------------
# Modelo Disponibilidad
# -------------------------------------------------
class Disponibilidad(models.Model):
    tarotista = models.ForeignKey(
        Tarotista,
        on_delete=models.CASCADE,
        related_name='disponibilidades'
    )

    # 0 = Lunes, 6 = Domingo (coincide con date.weekday())
    dia_semana = models.IntegerField(
        help_text="Día de la semana (0=Lunes, 6=Domingo)"
    )

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    reservado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        ordering = ['tarotista', 'dia_semana', 'hora_inicio']
        # Opcional (no obligatorio):
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['tarotista', 'dia_semana', 'hora_inicio', 'hora_fin'],
        #         name='unique_disponibilidad'
        #     )
        # ]

    def __str__(self):
        return (
            f"{self.tarotista} | "
            f"Día {self.dia_semana} "
            f"{self.hora_inicio} - {self.hora_fin}"
        )
