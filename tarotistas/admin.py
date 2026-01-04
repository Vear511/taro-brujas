from django.contrib import admin
from .models import Tarotista

@admin.register(Tarotista)
class TarotistaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_nombre',
        'disponible',
    )
    list_filter = ('disponible',)
    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
    )
    ordering = ('usuario__first_name',)

    def get_nombre(self, obj):
        """
        Retorna el nombre completo del usuario asociado al tarotista.
        Si no tiene usuario, retorna un guion.
        """
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return '—'

    get_nombre.short_description = 'Nombre del Tarotista'
