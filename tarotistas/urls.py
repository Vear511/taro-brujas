from django.urls import path
from . import views

app_name = 'tarotistas'

urlpatterns = [
    # Rutas existentes
    path('tarotistas/', views.lista_tarotistas, name='lista_tarotistas'),
    path('tarotista/<int:tarotista_id>/', views.perfil_tarotista, name='perfil_tarotista'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('bloquear-usuario/<int:usuario_id>/', views.bloquear_usuario, name='bloquear_usuario'),
    path('calendario/', views.calendario, name='calendario'),
    # En tu urls.py
    path('sobre-nosotras/', views.sobre_nosotras_view, name='sobre_nosotras'),
]
