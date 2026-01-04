from django.contrib import admin
from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'tarotista', 'paciente', 'estado', 'fecha_reporte')
    list_filter = ('estado', 'fecha_reporte', 'tarotista')
    search_fields = (
        'paciente__username',
        'paciente__first_name',
        'paciente__last_name',
        'tarotista__usuario__first_name'
    )
    readonly_fields = ('fecha_reporte', 'actualizado_en', 'cita')
    ordering = ('-fecha_reporte',)
    list_select_related = ('tarotista', 'paciente')

    fieldsets = (
        ('Información Principal', {
            'fields': ('tarotista', 'paciente', 'cita')
        }),
        ('Contenido', {
            'fields': ('experiencia',)
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Fechas', {
            'fields': ('fecha_reporte', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
