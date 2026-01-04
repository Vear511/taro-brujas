from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tarotistas.models import Tarotista

class Command(BaseCommand):
    help = 'Asocia el usuario azakana con un perfil de tarotista si no existe.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'azakana'
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuario {username} no existe.'))
            return
        if hasattr(user, 'tarotista'):
            self.stdout.write(self.style.SUCCESS(f'El usuario {username} ya tiene perfil de tarotista.'))
            return
        Tarotista.objects.create(usuario=user, descripcion='Auto-creado por script', disponible=True)
        self.stdout.write(self.style.SUCCESS(f'Perfil de tarotista creado para {username}.'))
