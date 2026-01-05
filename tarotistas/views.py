from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import Tarotista
from usuarios.models import Usuario
from citas.models import Cita


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

            # Crear tarotista (SOLO campos existentes)
            tarotista = Tarotista.objects.create(
                usuario=usuario,
                descripcion=request.POST.get('descripcion', ''),
                disponible=request.POST.get('disponible') == 'true'
            )

            return redirect('gestion_tarotistas')

        except Exception as e:
            return render(request, 'agregar_tarotista.html', {
                'error': f'Error al crear tarotista: {str(e)}'
            })

    return render(request, 'agregar_tarotista.html')


def lista_tarotistas(request):
    tarotistas = Tarotista.objects.filter(disponible=True)
    return render(request, 'lista_tarotistas.html', {
        'tarotistas': tarotistas
    })


def perfil_tarotista(request, tarotista_id):
    tarotista = get_object_or_404(Tarotista, id=tarotista_id)
    return render(request, 'perfil_tarotista.html', {
        'tarotista': tarotista
    })


@login_required
@user_passes_test(lambda u: hasattr(u, 'tarotista'))
def lista_clientes(request):
    clientes = Usuario.objects.exclude(
        tarotista__isnull=False
    ).exclude(
        is_staff=True
    )
    return render(request, 'lista_clientes.html', {
        'clientes': clientes
    })


@login_required
@user_passes_test(lambda u: hasattr(u, 'tarotista'))
def bloquear_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.bloqueado = not usuario.bloqueado
    usuario.save()
    return redirect('tarotistas:lista_clientes')


def calendario(request):
    print('DEBUG [tarotistas.views.calendario] usuario:', request.user)
    print('DEBUG [tarotistas.views.calendario] usuario.id:', getattr(request.user, 'id', None))
    print('DEBUG [tarotistas.views.calendario] usuario.username:', getattr(request.user, 'username', None))
    print('DEBUG [tarotistas.views.calendario] usuario.email:', getattr(request.user, 'email', None))
    print('DEBUG [tarotistas.views.calendario] usuario.is_authenticated:', getattr(request.user, 'is_authenticated', None))
    print('DEBUG [tarotistas.views.calendario] usuario model:', type(request.user))
    if hasattr(request.user, 'tarotista'):
        print('DEBUG [tarotistas.views.calendario] tarotista.id:', request.user.tarotista.id)
        print('DEBUG [tarotistas.views.calendario] tarotista.usuario.id:', request.user.tarotista.usuario.id)
    else:
        print('DEBUG [tarotistas.views.calendario] tarotista: NO ASOCIADO')

    import json
    from core.models import Disponibilidad
    from django.utils import timezone
    from datetime import datetime, timedelta
    eventos = []
    has_tarotista = hasattr(request.user, 'tarotista')
    tarotista_id = request.user.tarotista.id if has_tarotista else None
    if not has_tarotista:
        from django.contrib import messages
        messages.error(request, 'Solo tarotistas.')
        return redirect('core:home')
    horarios = Disponibilidad.objects.filter(tarotista=request.user.tarotista)
    today = timezone.now().date()
    js_today = (today.weekday() + 1) % 7
    for h in horarios:
        dias_hasta = (h.dia_semana - js_today) % 7
        fecha = today + timedelta(days=dias_hasta)
        start_dt = datetime.combine(fecha, h.hora_inicio)
        end_dt = datetime.combine(fecha, h.hora_fin)
        eventos.append({
            'id': h.id,
            'title': 'Reservado' if h.reservado else 'Disponible',
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'backgroundColor': '#dc3545' if h.reservado else '#28a745'
        })
    context = {
        'horarios_eventos_json': json.dumps(eventos),
        'total_horarios': horarios.count(),
        'horarios_disponibles': horarios.filter(reservado=False).count(),
        'horarios_reservados': horarios.filter(reservado=True).count(),
        'debug_has_tarotista': has_tarotista,
        'debug_tarotista_id': tarotista_id,
    }
    return render(request, 'calendario.html', context)
@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_tarotista(request, tarotista_id):
    """
    Permite a un administrador editar un tarotista existente.
    """
    tarotista = get_object_or_404(Tarotista, id=tarotista_id)

    if request.method == 'POST':
        try:
            # Editar campos del usuario
            usuario = tarotista.usuario
            usuario.first_name = request.POST.get('first_name', usuario.first_name)
            usuario.last_name = request.POST.get('last_name', usuario.last_name)
            usuario.email = request.POST.get('email', usuario.email)
            if request.POST.get('password'):
                usuario.set_password(request.POST['password'])
            usuario.save()

            # Editar campos del tarotista
            tarotista.descripcion = request.POST.get('descripcion', tarotista.descripcion)
            tarotista.disponible = request.POST.get('disponible') == 'true'
            tarotista.save()

            return redirect('tarotistas:lista_tarotistas')

        except Exception as e:
            return render(request, 'editar_tarotista.html', {'tarotista': tarotista, 'error': str(e)})

    return render(request, 'editar_tarotista.html', {'tarotista': tarotista})
@login_required
def lista_clientes(request):
    """
    Vista para que la tarotista vea la lista de sus clientes.
    Solo accesible para usuarias con es_tarotista = True.
    """
    # Seguridad extra: solo tarotistas
    if not getattr(request.user, "es_tarotista", False):
        messages.error(request, "Solo las tarotistas pueden acceder a la lista de clientes.")
        return redirect("core:home")

    # Obtenemos el perfil de Tarotista asociado al usuario
    try:
        tarotista = request.user.tarotista
    except Tarotista.DoesNotExist:
        messages.error(request, "Tu perfil de tarotista aún no está configurado.")
        return redirect("core:home")

    # Sacamos las citas de esa tarotista y obtenemos clientes únicos
    # Usamos DISTINCT ON en PostgreSQL (Railway usa Postgres)
    citas_distintas = (
        Cita.objects
        .filter(tarotista=tarotista)
        .select_related("cliente")
        .order_by("cliente_id")              # requerido para distinct("cliente_id")
        .distinct("cliente_id")
    )

    clientes = [cita.cliente for cita in citas_distintas]

    return render(request, "lista_clientes.html", {
        "clientes": clientes,
    })


@login_required
def bloquear_usuario(request, usuario_id):
    """
    Permite a la tarotista bloquear / desbloquear un cliente.
    Usa el campo booleano 'bloqueado' del modelo Usuario.
    """
    if not getattr(request.user, "es_tarotista", False):
        messages.error(request, "Solo las tarotistas pueden bloquear clientes.")
        return redirect("core:home")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Toggle del estado
    usuario.bloqueado = not getattr(usuario, "bloqueado", False)
    usuario.save(update_fields=["bloqueado"])

    nombre = usuario.get_full_name() or usuario.username

    if usuario.bloqueado:
        messages.success(request, f"Has bloqueado a {nombre}. Ya no podrá iniciar sesión.")
    else:
        messages.success(request, f"Has desbloqueado a {nombre}. Podrá volver a iniciar sesión.")

    return redirect("tarotistas:lista_clientes")
