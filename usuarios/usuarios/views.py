from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from usuarios.models import Usuario

def registro(request):
    if request.method == 'POST':
        # Crear usuario manualmente
        try:
            # Verificar que las contraseñas coincidan
            if request.POST['password1'] != request.POST['password2']:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'registration/registro.html')
            
            # Crear el usuario
            usuario = Usuario.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password1'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name']
            )
            
            # Iniciar sesión automáticamente
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a {usuario.first_name}! Cuenta creada exitosamente.')
            return redirect('home')  # Redirigir a la página principal
            
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, 'registration/registro.html')
    
    return render(request, 'registration/registro.html')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    return render(request, 'perfil.html')

#@login_required
#def editar_perfil(request):
#    return render(request, 'editar_perfil.html')  # Puedes crear este template después


@login_required
def editar_perfil(request):
    """Permite al usuario editar campos básicos de su perfil.

    Nota: el template `gestionperfil.html` espera algunos campos (por ejemplo
    `avatar`, `bio`, `telefono`). Aquí actualizamos los campos existentes en
    `Usuario`. Si necesitas un modelo `Perfil` separado, podemos adaptarlo.
    """
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        user.telefono = request.POST.get('telefono', user.telefono)

        # Manejar avatar si se sube
        if 'imagen' in request.FILES:
            # El template usa el campo 'imagen' para el input; el modelo usa 'avatar'
            user.avatar = request.FILES['imagen']

        # Manejar apodo
        user.apodo = request.POST.get('apodo', user.apodo)

        user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('usuarios:perfil')

    return render(request, 'gestionperfil.html')
