# tarotistas/admin.py
from django.contrib import admin
from .models import Tarotista

@admin.register(Tarotista)
class TarotistaAdmin(admin.ModelAdmin):
    list_display = ('get_nombre', 'especialidad', 'experiencia', 'precio_por_sesion', 'disponible')
    list_filter = ('disponible', 'especialidad')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')
    
    def get_nombre(self, obj):
        return obj.usuario.get_full_name()
    get_nombre.short_description = 'Nombre'