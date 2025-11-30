# usuarios/urls.py

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # ... rutas de registro/perfil (manteniendo las tuyas) ...
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # Rutas de Administración de Usuarios
    path('admin/lista/', views.usuarios_lista, name='usuarios_lista'),
    path('admin/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('admin/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Rutas de Baneo
    path('admin/banear/<int:usuario_id>/', views.banear_usuario, name='banear_usuario'),
    path('admin/desbanear/<int:usuario_id>/', views.desbanear_usuario, name='desbanear_usuario'),
]
