from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('servicios/', views.servicios, name='servicios'),
    path('sobre-nosotras/', views.sobre_nosotras, name='sobre_nosotras'),
    
    # URLs de reportes
    path('reportes/', views.reportes_lista, name='reportes'),
    path('reportes/crear/', views.crear_reporte, name='crear_reporte'),
    path('reportes/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('reportes/<int:reporte_id>/editar/', views.editar_reporte, name='editar_reporte'),
    path('reportes/<int:reporte_id>/eliminar/', views.eliminar_reporte, name='eliminar_reporte'),
]