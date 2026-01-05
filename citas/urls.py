from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # Agendar una nueva cita
    path('agendar/', views.agendar_cita, name='agendar_cita'),

    # Listado de citas (ejemplo)
    path('mis-citas/', views.mis_citas, name='mis_citas'),

    # Detalle de cita (ejemplo)
    path('<int:cita_id>/', views.detalle_cita, name='detalle_cita'),

    # Editar cita (ejemplo)
    path('<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),

    # Cancelar/eliminar cita (ejemplo)
    path('<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
]
