# tarotistas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.models import Usuario
from .models import Tarotista

@user_passes_test(lambda u: u.is_staff)
def agregar_tarotista(request):
    if request.method == 'POST':
        try:
            # Crear usuario
            usuario = Usuario.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name']
            )
            
            # Crear tarotista
            tarotista = Tarotista.objects.create(
                usuario=usuario,
                especialidad=request.POST['especialidad'],
                experiencia=int(request.POST['experiencia']),
                precio_por_sesion=float(request.POST['precio_por_sesion']),
                descripcion=request.POST['descripcion'],
                disponible=request.POST['disponible'] == 'true'
            )
            
            return redirect('gestion_tarotistas')
            
        except Exception as e:
            # Manejar errores (usuario ya existe, etc.)
            return render(request, 'agregar_tarotista.html', {
                'error': f'Error al crear tarotista: {str(e)}'
            })
    
    return render(request, 'agregar_tarotista.html')

def lista_tarotistas(request):
    tarotistas = Tarotista.objects.filter(disponible=True)
    return render(request, 'lista_tarotistas.html', {'tarotistas': tarotistas})

def perfil_tarotista(request, tarotista_id):
    tarotista = Tarotista.objects.get(id=tarotista_id)
    return render(request, 'perfil_tarotista.html', {'tarotista': tarotista})

@login_required
@user_passes_test(lambda u: hasattr(u, 'tarotista'))
def lista_clientes(request):
    # Obtener todos los usuarios que no son tarotistas ni staff
    clientes = Usuario.objects.exclude(tarotista__isnull=False).exclude(is_staff=True)
    return render(request, 'lista_clientes.html', {'clientes': clientes})

@login_required
@user_passes_test(lambda u: hasattr(u, 'tarotista'))
def bloquear_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.bloqueado = not usuario.bloqueado
    usuario.save()
    return redirect('tarotistas:lista_clientes')
