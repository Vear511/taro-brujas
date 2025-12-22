from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
# Importamos el modelo Usuario. Asumo que está en el mismo nivel que views.py
from .models import Usuario 


def registro(request):
    """
    Vista para manejar el registro de nuevos usuarios.
    Crea el usuario y realiza el inicio de sesión automático.
    """
    if request.method == 'POST':
        # Crear usuario manualmente
        try:
            # 1. Verificar que las contraseñas coincidan
            if request.POST['password1'] != request.POST['password2']:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'registration/registro.html')
            
            # 2. Crear el usuario en la base de datos
            usuario = Usuario.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password1'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name']
            )
            
            # ------------------------------------------------------------------
            # LA CORRECCIÓN CRÍTICA: 
            # Asignar el backend de autenticación antes de llamar a login(). 
            # Esto resuelve el error "You have multiple authentication backends configured".
            usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            # ------------------------------------------------------------------
            
            # 3. Iniciar sesión automáticamente
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a {usuario.first_name}! Cuenta creada exitosamente.')
            return redirect('home')  # Redirigir a la página principal
            
        except Exception as e:
            # Captura y muestra cualquier otro error (ej. nombre de usuario duplicado)
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, 'registration/registro.html')
    
    return render(request, 'registration/registro.html')


from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    """Muestra la página de perfil del usuario."""
    return render(request, 'perfil.html')

@login_required
def editar_perfil(request):
    """Permite al usuario editar campos básicos de su perfil."""
    user = request.user

    if request.method == 'POST':
        # Actualizar campos básicos
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        
        # Actualizar campos personalizados (asegúrate de que existan en tu modelo Usuario)
        user.bio = request.POST.get('bio', getattr(user, 'bio', ''))
        user.telefono = request.POST.get('telefono', getattr(user, 'telefono', ''))
        user.apodo = request.POST.get('apodo', getattr(user, 'apodo', ''))

        # Manejar la subida de la imagen (avatar)
        if 'imagen' in request.FILES:
            user.avatar = request.FILES['imagen']

        user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('usuarios:perfil')

    return render(request, 'gestionperfil.html')
