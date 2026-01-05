from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('servicios/', views.servicios, name='servicios'),
    path('sobre-nosotras/', views.sobre_nosotras, name='sobre_nosotras'),
    
    # URLs de Disponibilidad del Calendario (NUEVAS RUTAS) 📅
    path('calendario-disponibilidad/', views.calendario_disponibilidad_view, name='calendario_disponibilidad'),
    path('disponibilidad-ajax/', views.manejar_disponibilidad_ajax, name='manejar_disponibilidad_ajax'),
    # Las funciones 'calendario_disponibilidad_view' y 'manejar_disponibilidad_ajax' 
    # deben existir en tu archivo 'views.py'.
    
    path('toma-horas/', views.toma_de_horas, name='toma_de_horas'),


    # Nueva ruta para horarios disponibles
    path('calendario/horarios/', views.horarios_disponibles_json, name='horarios_disponibles_json'),
    # Endpoint para reservar horario
    path('calendario/reservar/', views.reservar_horario, name='reservar_horario'),


    # URLs de reportes
    path('reportes/', views.reportes_lista, name='reportes'),
    path('reportes/crear/', views.crear_reporte, name='crear_reporte'),
    path('reportes/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('reportes/<int:reporte_id>/editar/', views.editar_reporte, name='editar_reporte'),
    path('reportes/<int:reporte_id>/eliminar/', views.eliminar_reporte, name='eliminar_reporte'),
]
