from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario

@receiver(post_save, sender=Usuario)
def usuario_creado(sender, instance, created, **kwargs):
    if created:
        print(f'Usuario creado: {instance.username}')
