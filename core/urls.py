from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ==================== VISTAS GENERALES ====================
    path('', views.home, name='home'),
    path('servicios/', views.servicios, name='servicios'),
    path('sobre-nosotras/', views.sobre_nosotras, name='sobre_nosotras'),

    # ==================== DISPONIBILIDAD (TAROTISTAS) ====================
    path(
        'calendario-disponibilidad/',
        views.calendario_disponibilidad_view,
        name='calendario_disponibilidad'
    ),
    path(
        'disponibilidad-ajax/',
        views.manejar_disponibilidad_ajax,
        name='manejar_disponibilidad_ajax'
    ),

    # ==================== TOMA DE HORAS (CLIENTES) ====================
    path(
        'toma-horas/',
        views.toma_de_horas,
        name='toma_de_horas'
    ),
    path(
        'reservar-hora-ajax/',
        views.reservar_hora_ajax,
        name='reservar_hora_ajax'
    ),

    # ==================== REPORTES ====================
    path('reportes/', views.reportes_lista, name='reportes'),
    path('reportes/crear/', views.crear_reporte, name='crear_reporte'),
    path('reportes/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('reportes/<int:reporte_id>/editar/', views.editar_reporte, name='editar_reporte'),
    path('reportes/<int:reporte_id>/eliminar/', views.eliminar_reporte, name='eliminar_reporte'),
]
