from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
# En tu app de tarotistas (ej. tarotistas/apps.py)
from django.apps import AppConfig

class TarotistasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tarotistas'

    # ESTA LÍNEA ES CLAVE: Importa el módulo de señales al iniciar la app.
    def ready(self):
        import tarotistas.signals
