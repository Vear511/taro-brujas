from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # ------------------------------------
    # Rutas Públicas (Registro y Perfil)
    # ------------------------------------
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # ------------------------------------
    # Rutas de Administración de Usuarios (Nuevas)
    # ------------------------------------
    # Listado principal para la gestión de usuarios
    path('admin/lista/', views.usuarios_lista, name='usuarios_lista'), 
    
    # Edición de otros usuarios (No es el perfil propio)
    path('admin/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),

    # Eliminación de usuario (Requiere vista 'eliminar_usuario' con método POST)
    path('admin/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # 🔨 Rutas de Baneo Agregadas (Requieren vistas 'banear_usuario' y 'desbanear_usuario')
    path('admin/banear/<int:usuario_id>/', views.banear_usuario, name='banear_usuario'),
    path('admin/desbanear/<int:usuario_id>/', views.desbanear_usuario, name='desbanear_usuario'),
]
