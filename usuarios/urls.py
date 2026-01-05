from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Registro y autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Restablecimiento de contraseña
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password-reset/form/', views.password_reset_form, name='password_reset_form'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),

    # Perfil de usuario logueado
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # Rutas opcionales para administración de usuarios
    # path('<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    # path('<int:usuario_id>/editar/', views.editar_usuario_admin, name='editar_usuario_admin'),
]
