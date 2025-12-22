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

    # URLs de reportes
    path('reportes/', views.reportes_lista, name='reportes'),
    path('reportes/crear/', views.crear_reporte, name='crear_reporte'),
    path('reportes/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('reportes/<int:reporte_id>/editar/', views.editar_reporte, name='editar_reporte'),
    path('reportes/<int:reporte_id>/eliminar/', views.eliminar_reporte, name='eliminar_reporte'),
    path('sobre-nosotras/', views.sobre_nosotras, name='sobre_nosotras'), # ¡Asegúrate de que no haya un 'view' aquí!
]
