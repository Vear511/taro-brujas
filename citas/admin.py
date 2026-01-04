from django.contrib import admin
from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'tarotista',
        'fecha_hora',
        'estado',
    )

    list_filter = (
        'estado',
        'fecha_hora',
    )

    search_fields = (
        'cliente__username',
        'tarotista__usuario__username',
    )

    ordering = ('-fecha_hora',)
    list_per_page = 25
