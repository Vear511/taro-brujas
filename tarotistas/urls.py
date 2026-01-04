from django.urls import path
from . import views

app_name = 'tarotistas'

urlpatterns = [
    # Tarotistas
    path('', views.lista_tarotistas, name='lista_tarotistas'),  # lista principal
    path('<int:tarotista_id>/', views.perfil_tarotista, name='perfil_tarotista'),
    path('<int:tarotista_id>/editar/', views.editar_tarotista, name='editar_tarotista'),  # si existe edición

    # Clientes de tarotista
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/bloquear/<int:usuario_id>/', views.bloquear_usuario, name='bloquear_usuario'),

    # Calendario
    path('calendario/', views.calendario, name='calendario'),
]
