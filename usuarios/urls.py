from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm # Si usas el formulario de login estándar
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm # Asume la existencia de tu RegistroForm

# Importaciones de modelos (si las usas directamente en otras vistas)
# from .models import Usuario 
# from tarotistas.models import Tarotista 

# ----------------------------------------------------
# 1. VISTA DE REGISTRO (CON LA CORRECCIÓN DE LOGIN)
# ----------------------------------------------------

def registro(request):
    """
    Maneja el registro de nuevos usuarios.
    Corrige el error de "multiple authentication backends" al loguear.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # Guarda el nuevo usuario (objeto Usuario)
            user = form.save() 
            
            # === CORRECCIÓN CLAVE: ESPECIFICAR EL BACKEND ===
            # Esto resuelve el error "You have multiple authentication backends..."
            login(
                request, 
                user, 
                backend='django.contrib.auth.backends.ModelBackend' 
            )
            
            messages.success(request, f'¡Bienvenido/a {user.first_name}! Tu cuenta ha sido creada y has iniciado sesión.')
            return redirect('home') # Redirige al inicio o donde sea apropiado
        else:
            # Manejo de errores detallado
            for field, error_list in form.errors.items():
                for error in error_list:
                    # Formatea el error para que sea amigable (ej: "Error en username: Ya existe.")
                    messages.error(request, f"Error en {field}: {error}")
    else:
        form = RegistroForm()
        
    return render(request, 'usuarios/registro.html', {'form': form})

# ----------------------------------------------------
# 2. VISTA DE LOGIN Y LOGOUT (Ejemplo, si no usas las de Django)
# ----------------------------------------------------

def login_view(request):
    """Maneja el inicio de sesión."""
    if request.method == 'POST':
        # Usa AuthenticationForm para validar el usuario/contraseña
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # authenticate usa todos los backends, incluyendo el BloqueadoBackend
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.info(request, f"Iniciaste sesión como {username}.")
                return redirect('home')
            else:
                messages.error(request,"Nombre de usuario o contraseña incorrectos.")
        else:
            messages.error(request,"Nombre de usuario o contraseña incorrectos.")
    
    form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'login_form': form})

def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('home') # Redirige a la página de inicio

# ----------------------------------------------------
# 3. VISTAS DE PERFIL Y EDICIÓN
# ----------------------------------------------------

@login_required
def perfil(request):
    """Muestra el perfil del usuario autenticado."""
    return render(request, 'usuarios/perfil.html')

@login_required
def editar_perfil(request):
    """Permite editar el perfil del usuario autenticado."""
    # Nota: Aquí deberías implementar la lógica con un formulario de edición de perfil.
    # user_form = UsuarioEditForm(instance=request.user)
    # ...
    return render(request, 'usuarios/editar_perfil.html')
