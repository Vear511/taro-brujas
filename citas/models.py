from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from usuarios.models import Usuario
from tarotistas.models import Tarotista


class Cita(models.Model):
    SERVICIOS = [
        ('basico', 'Tarot Básico'),
        ('completo', 'Tarot Completo'),
        ('amor', 'Tarot del Amor'),
        ('karmico', 'Tarot Kármico'),
    ]

    servicio = models.CharField(max_length=20, choices=SERVICIOS, default='basico')
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='citas_cliente'
    )
    tarotista = models.ForeignKey(
        Tarotista,
        on_delete=models.CASCADE,
        related_name='citas_tarotista'
    )
    fecha_hora = models.DateTimeField()
    duracion = models.PositiveIntegerField(default=60)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['tarotista', 'fecha_hora']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tarotista', 'fecha_hora'],
                name='unique_cita_tarotista_fecha'
            )
        ]

    def clean(self):
        if self.fecha_hora < timezone.now():
            raise ValidationError("No se pueden crear citas en el pasado.")

        if self.duracion <= 0 or self.duracion > 240:
            raise ValidationError("La duración debe ser entre 1 y 240 minutos.")

    def __str__(self):
        return f"Cita #{self.id} | {self.cliente} → {self.tarotista} | {self.fecha_hora}"
