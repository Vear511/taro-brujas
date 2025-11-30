from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.models import Usuario
from .models import Tarotista

# ----------------------------------------------------------------------
# VISTAS PÚBLICAS Y DE CONSULTA DE TAROTISTAS
# ----------------------------------------------------------------------

def sobre_nosotras_view(request):
    """
    Vista que recupera los datos combinados (Usuario + Tarotista) para
    la sección pública 'Conoce a nuestras tarotistas'.
    Incluye lógica de diagnóstico para verificar la carga de datos.
    """
    
    # 1. PRUEBA DE CONSULTA: Usar .all() es la mejor forma de descartar fallos de filtro.
    # Si esta línea falla, el problema es en la relación del modelo (ForeignKey/OneToOneField).
    tarotistas_data = Tarotista.objects.select_related('usuario').all()
    
    # *** DIAGNÓSTICO: Buscar esto en la consola después de visitar la URL ***
    print(f"--- INICIO DIAGNÓSTICO SOBRE_NOSOTRAS ---")
    print(f"Número de tarotistas encontradas (SIN FILTRO): {tarotistas_data.count()}")
    
    tarotistas_listos = []
    
    for t in tarotistas_data:
        try:
            # Mapeamos los campos a un diccionario para el template
            tarotistas_listos.append({
                'nombre': t.usuario.first_name, 
                'descripcion': t.descripcion, 
                # Usamos .url para campos FileField/ImageField
                'url_imagen': t.usuario.avatar.url if t.usuario.avatar else '/static/img/placeholder_default.png', 
            })
        except AttributeError:
            # Se dispara si un registro de Tarotista no tiene un Usuario válido asociado.
            print(f"ERROR DE BD: El registro de Tarotista (ID: {t.id}) tiene un usuario_id roto o nulo.")
            continue # Saltar este registro para no romper la página
        
    print(f"Lista final para el template: {tarotistas_listos}")
    print(f"--- FIN DIAGNÓSTICO SOBRE_NOSOTRAS ---")
        
    context = {
        'tarotistas': tarotistas_listos
    }
    
    return render(request, 'sobre_nosotras.html', context)


def lista_tarotistas(request):
    """
    Vista original para listar tarotistas disponibles.
    (Si usas 'sobre_nosotras_view' para el listado público, esta podría ser redundante)
    """
    tarotistas = Tarotista.objects.filter(disponible=True)
    return render(request, 'lista_tarotistas.html', {'tarotistas': tarotistas})


def perfil_tarotista(request, tarotista_id):
    tarotista = Tarotista.objects.get(id=tarotista_id)
    return render(request, 'perfil_tarotista.html', {'tarotista': tarotista})


# ----------------------------------------------------------------------
# VISTAS DE GESTIÓN Y ADMINISTRACIÓN (Requieren login o permisos)
# ----------------------------------------------------------------------

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
