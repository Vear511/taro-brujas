from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from usuarios.models import Usuario
from tarotistas.models import Tarotista
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.conf.urls.static import static
import re

# ---------------------------
# Decoradores y validadores
# ---------------------------
def admin_required(function):
    return user_passes_test(lambda u: u.is_staff)(function)

def validar_rut(rut):
    """
    Valida un RUT chileno.
    Retorna True si es válido, False si no.
    """
    rut = rut.replace(".", "").replace("-", "").strip().upper()
    if not re.match(r'^\d{7,8}[0-9K]$', rut):
        return False

    numero = rut[:-1]
    dv_ingresado = rut[-1]

    suma = 0
    multiplicador = 2
    for digit in reversed(numero):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    dv_calculado = 11 - (suma % 11)
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)

    return dv_calculado == dv_ingresado

# ---------------------------
# Vistas principales
# ---------------------------
def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')

def perfil(request):
    return render(request, 'perfil.html')

def agendar_cita(request):
    return render(request, 'agendar_cita.html')

def mis_citas(request):
    return render(request, 'mis_citas.html')

# ---------------------------
# Vista de registro
# ---------------------------
def registro(request):
    data = {}
    errores = {}

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        data = {
            'rut': rut,
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }

        # Validaciones
        if not first_name:
            errores['first_name'] = 'Nombre requerido.'
        if not last_name:
            errores['last_name'] = 'Apellido requerido.'

        if not validar_rut(rut):
            errores['rut'] = 'RUT inválido.'
        if Usuario.objects.filter(rut=rut).exists():
             errores['rut'] = 'Este rut de usuario ya está en uso.'

        if Usuario.objects.filter(username=username).exists():
            errores['username'] = 'Este nombre de usuario ya está en uso.'

        if Usuario.objects.filter(email=email).exists():
            errores['email'] = 'Este email ya está registrado.'

        if password1 != password2:
            errores['password'] = 'Las contraseñas no coinciden.'
        elif len(password1) < 10 or \
             not re.search(r'[A-Z]', password1) or \
             not re.search(r'\d', password1) or \
             not re.search(r'[!@#$%&*]', password1):
            errores['password'] = 'Contraseña no cumple los requisitos mínimos.'

        if errores:
            return render(request, 'registro.html', {'data': data, 'errores': errores})

        try:
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                rut=rut
            )
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a {usuario.first_name}! Cuenta creada exitosamente.')
            return redirect('home')
        except Exception as e:
            errores['general'] = f'Error al crear la cuenta: {str(e)}'
            return render(request, 'registro.html', {'data': data, 'errores': errores})

    return render(request, 'registro.html', {'data': {}, 'errores': {}})

# ---------------------------
# Vistas administración
# ---------------------------
@admin_required
def gestion_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'admin/gestion_usuarios.html', {'usuarios': usuarios})

@admin_required
def gestion_tarotistas(request):
    tarotistas = Tarotista.objects.all()
    return render(request, 'admin/gestion_tarotistas.html', {'tarotistas': tarotistas})

@admin_required
def agregar_tarotista(request):
    return render(request, 'admin/agregar_tarotista.html')

@admin_required
def editar_tarotista(request, tarotista_id):
    return render(request, 'admin/editar_tarotista.html', {'tarotista_id': tarotista_id})

@admin_required
def editar_usuario(request, usuario_id):
    return render(request, 'admin/editar_usuario.html', {'usuario_id': usuario_id})

# ---------------------------
# URLs
# ---------------------------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('servicios/', servicios, name='servicios'),
    path('sobre-nosotras/', sobre_nosotras, name='sobre_nosotras'),
    path('registro/', registro, name='registro'),
    path('perfil/', perfil, name='perfil'),
    path('citas/agendar/', agendar_cita, name='agendar_cita'),
    path('citas/mis-citas/', mis_citas, name='mis_citas'),
    
    # URLs de autenticación
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # URLs de administración
    path('admin-panel/gestion-usuarios/', gestion_usuarios, name='gestion_usuarios'),
    path('admin-panel/gestion-tarotistas/', gestion_tarotistas, name='gestion_tarotistas'),
    path('admin-panel/agregar-tarotista/', agregar_tarotista, name='agregar_tarotista'),
    path('admin-panel/editar-tarotista/<int:tarotista_id>/', editar_tarotista, name='editar_tarotista'),
    path('admin-panel/editar-usuario/<int:usuario_id>/', editar_usuario, name='editar_usuario'),
]

# Incluir las URLs de las apps que usan namespacing
urlpatterns += [
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('core/', include(('core.urls', 'core'), namespace='core')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
