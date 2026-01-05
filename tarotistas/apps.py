from django.apps import AppConfig

class TarotistasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tarotistas'

    def ready(self):
        import tarotistas.signals
