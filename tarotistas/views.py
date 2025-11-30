# tarotistas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.models import Usuario
from .models import Tarotista

# --- NUEVA FUNCIÓN PARA LA PÁGINA "SOBRE NOSOTRAS" ---

def sobre_nosotras_view(request):
    """
    Vista que recupera los datos combinados (JOIN) de las tablas Tarotista y Usuario
    para mostrarlos en la sección "Conoce a nuestras tarotistas".
    """
    
    # 1. Realiza la consulta JOIN usando select_related()
    # Filtramos por cuentas de usuario activas y que sean tarotistas disponibles (opcional)
    tarotistas_data = Tarotista.objects.select_related('usuario').filter(
        usuario__is_active=True,
        disponible=True # Filtra solo las tarotistas marcadas como disponibles
    ).all()
    
    tarotistas_listos = []
    
    for t in tarotistas_data:
        # 2. Mapea los campos al formato esperado por el template
        tarotistas_listos.append({
            'nombre': t.usuario.first_name, 
            'descripcion': t.descripcion, 
            # Asegúrate que la ruta de la imagen sea accesible. Usamos .url para campos FileField/ImageField
            'url_imagen': t.usuario.avatar.url if t.usuario.avatar else '/static/img/placeholder_default.png', 
        })
        
    context = {
        'tarotistas': tarotistas_listos
    }
    
    return render(request, 'sobre_nosotras.html', context)


# ----------------------------------------------------
# A continuación, el resto de tus vistas ya existentes:

@user_passes_test(lambda u: u.is_staff)
def agregar_tarotista(request):
# ... (Tu código existente para agregar_tarotista) ...
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
def calendario(request):
    """
    Vista del calendario para la gestión de disponibilidad y citas de la tarotista.
    """
    # Lógica futura para obtener citas, disponibilidad, etc.
    context = {
        'tarotista': request.user.tarotista if hasattr(request.user, 'tarotista') else None,
        # ... más datos del calendario
    }
    return render(request, 'calendario.html', context)
