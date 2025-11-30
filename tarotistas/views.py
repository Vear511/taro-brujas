from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from usuarios.models import Usuario
from .models import Tarotista

# ---------------------------
# Decorador Personalizado
# ---------------------------

def tarotista_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='home'):
    '''
    Decorador para vistas que verifica que el usuario esté autenticado y sea una tarotista.
    Redirige al home si no cumple los requisitos.
    '''
    actual_decorator = user_passes_test(
        # La condición verifica que el usuario esté autenticado Y que tenga el atributo 'es_tarotista' True.
        # Asumiendo que has añadido 'es_tarotista' como propiedad o campo en tu modelo Usuario.
        # Si usas el modelo Tarotista relacionado, usa: lambda u: u.is_authenticated and hasattr(u, 'tarotista')
        lambda u: u.is_authenticated and getattr(u, 'es_tarotista', False), 
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# ---------------------------
# Vistas existentes
# ---------------------------

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

# Nota: Cambié el decorador de 'hasattr(u, 'tarotista')' a 'tarotista_required'
@tarotista_required
def lista_clientes(request):
    # Obtener todos los usuarios que no son tarotistas ni staff
    clientes = Usuario.objects.exclude(tarotista__isnull=False).exclude(is_staff=True)
    return render(request, 'lista_clientes.html', {'clientes': clientes})

@tarotista_required
def bloquear_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.bloqueado = not usuario.bloqueado
    usuario.save()
    return redirect('tarotistas:lista_clientes')

# ---------------------------
# VISTA NUEVA: CALENDARIO
# ---------------------------

@tarotista_required
def calendario(request):
    """
    Vista del calendario para la gestión de disponibilidad y citas de la tarotista.
    """
    # Lógica futura para obtener citas, disponibilidad, etc.
    context = {
        'tarotista': request.user.tarotista if hasattr(request.user, 'tarotista') else None,
        # ... más datos del calendario
    }
    return render(request, 'tarotistas/calendario.html', context)
