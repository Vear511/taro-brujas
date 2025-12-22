from datetime import datetime, timedelta, date
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

# Modelos
from .models import Reporte, Disponibilidad
from citas.models import Cita
from usuarios.models import Usuario
from tarotistas.models import Tarotista
from django.db.models import Q

# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')


@login_required
def reportes_lista(request):
    q = request.GET.get('q', '').strip()
    order = request.GET.get('order', 'desc')

    if hasattr(request.user, 'tarotista'):
        tarotista = request.user.tarotista
        reportes = Reporte.objects.filter(tarotista=tarotista)
    else:
        reportes = Reporte.objects.filter(paciente=request.user)

    if q:
        try:
            reportes = reportes.filter(
                Q(paciente__username__icontains=q) |
                Q(paciente__first_name__icontains=q) |
                Q(paciente__last_name__icontains=q) |
                Q(experiencia__icontains=q)
            )
        except Exception as e:
            messages.error(request, 'Ocurrió un error al realizar la búsqueda.')
            print("Error en búsqueda:", e)
            reportes = Reporte.objects.none()

    reportes = reportes.order_by('fecha_reporte' if order == 'asc' else '-fecha_reporte')
    search_no_results = bool(q) and (not reportes.exists())

    context = {
        'reportes': reportes,
        'reportes_recientes': list(reportes[:3]),
        'q': q,
        'order': order,
        'search_no_results': search_no_results,
    }
    return render(request, 'reportes.html', context)


@login_required
def crear_reporte(request):
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden crear reportes.')
        return redirect('perfil')

    tarotista = request.user.tarotista

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        experiencia = request.POST.get('experiencia')
        cita_id = request.POST.get('cita_id', '')

        if not paciente_id or not experiencia:
            messages.error(request, 'Por favor completa todos los campos requeridos.')
            citas = Cita.objects.filter(tarotista=tarotista, estado='completada')
            pacientes = Usuario.objects.filter(tarotista__isnull=True)
            return render(request, 'crear_reporte.html', {'citas': citas, 'pacientes': pacientes})

        try:
            paciente = get_object_or_404(Usuario, id=paciente_id)
            cita = get_object_or_404(Cita, id=cita_id) if cita_id else None

            Reporte.objects.create(
                tarotista=tarotista,
                paciente=paciente,
                cita=cita,
                experiencia=experiencia,
            )

            messages.success(request, 'Reporte creado exitosamente.')
            return redirect('core:reportes')

        except Exception as e:
            messages.error(request, f'Error al crear el reporte: {str(e)}')
            return redirect('core:crear_reporte')

    citas = Cita.objects.filter(tarotista=tarotista, estado='completada')
    pacientes = Usuario.objects.all()

    return render(request, 'crear_reporte.html', {'citas': citas, 'pacientes': pacientes})


@login_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)

    if hasattr(request.user, 'tarotista') and reporte.tarotista.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver este reporte.')
        return redirect('core:reportes')
    elif not hasattr(request.user, 'tarotista') and reporte.paciente != request.user:
        messages.error(request, 'No tienes permiso para ver este reporte.')
        return redirect('core:reportes')

    return render(request, 'detalle_reporte.html', {'reporte': reporte})


@login_required
def editar_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)

    if reporte.tarotista.usuario != request.user:
        messages.error(request, 'No tienes permiso para editar este reporte.')
        return redirect('core:reportes')

    if request.method == 'POST':
        try:
            reporte.experiencia = request.POST.get('experiencia', reporte.experiencia)
            estado = request.POST.get('estado', reporte.estado)
            if estado in ['abierto', 'cerrado']:
                reporte.estado = estado
            reporte.save()
            messages.success(request, 'Reporte actualizado exitosamente.')
            return redirect('core:detalle_reporte', reporte_id=reporte.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar el reporte: {str(e)}')

    return render(request, 'editar_reporte.html', {'reporte': reporte})


@login_required
def eliminar_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)

    if reporte.tarotista.usuario != request.user:
        messages.error(request, 'No tienes permiso para eliminar este reporte.')
        return redirect('core:reportes')

    if request.method == 'POST':
        reporte.delete()
        messages.success(request, 'Reporte eliminado exitosamente.')
        return redirect('core:reportes')

    return render(request, 'confirmar_eliminar_reporte.html', {'reporte': reporte})


# ==================== VISTAS DE CALENDARIO ====================

def calendario_disponibilidad_view(request):
    """
    Muestra el calendario con TODAS las horas disponibles de todos los tarotistas.
    """
    # Obtener todos los horarios
    horarios = Disponibilidad.objects.all()

    # Calcular fecha del lunes de la semana actual
    hoy = date.today()
    lunes_semana = hoy - timedelta(days=hoy.weekday())

    eventos_fc = []
    for h in horarios:
        fecha_evento = lunes_semana + timedelta(days=h.dia_semana)
        start_dt = make_aware(datetime.combine(fecha_evento, h.hora_inicio))
        end_dt = make_aware(datetime.combine(fecha_evento, h.hora_fin))

        eventos_fc.append({
            'id': h.pk,
            'title': f'{h.tarotista.usuario.get_full_name()} - ' + ('Reservado' if h.reservado else 'Disponible'),
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'extendedProps': {
                'is_reserved': h.reservado,
                'tarotista_id': h.tarotista.id
            },
        })

    horarios_eventos_json = json.dumps(eventos_fc)

    context = {
        'total_horarios': horarios.count(),
        'horarios_disponibles': horarios.filter(reservado=False).count(),
        'horarios_reservados': horarios.filter(reservado=True).count(),
        'horarios_eventos_json': horarios_eventos_json,
    }
    return render(request, 'calendario.html', context)


@require_POST
@login_required
@csrf_exempt
def manejar_disponibilidad_ajax(request):
    """Permite eliminar horarios disponibles vía AJAX."""
    if not hasattr(request.user, 'tarotista'):
        return JsonResponse({'success': False, 'error': 'Permiso denegado.'}, status=403)

    try:
        data = json.loads(request.body)
        action = data.get('action')
        tarotista = request.user.tarotista

        if action == 'delete':
            event_id = data.get('event_id')
            horario = Disponibilidad.objects.get(pk=event_id, tarotista=tarotista, reservado=False)
            horario.delete()
            return JsonResponse({'success': True, 'message': 'Horario eliminado'})
        else:
            return JsonResponse({'success': False, 'error': 'Acción no válida'}, status=400)

    except Disponibilidad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Horario no encontrado o ya reservado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'}, status=500)


def toma_de_horas(request):
    return render(request, 'toma_de_horas.html')
