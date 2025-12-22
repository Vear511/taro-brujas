from datetime import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q

# ==================== MODELOS ====================

from .models import Reporte, Disponibilidad
from citas.models import Cita
from usuarios.models import Usuario
from tarotistas.models import Tarotista

# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')

# ==================== REPORTES ====================

@login_required
def reportes_lista(request):
    q = request.GET.get('q', '').strip()
    order = request.GET.get('order', 'desc')

    if hasattr(request.user, 'tarotista'):
        reportes = Reporte.objects.filter(tarotista=request.user.tarotista)
    else:
        reportes = Reporte.objects.filter(paciente=request.user)

    if q:
        reportes = reportes.filter(
            Q(paciente__username__icontains=q) |
            Q(paciente__first_name__icontains=q) |
            Q(paciente__last_name__icontains=q) |
            Q(experiencia__icontains=q)
        )

    reportes = reportes.order_by('fecha_reporte' if order == 'asc' else '-fecha_reporte')

    context = {
        'reportes': reportes,
        'q': q,
        'order': order,
        'search_no_results': bool(q and not reportes.exists())
    }
    return render(request, 'reportes.html', context)

# ==================== DISPONIBILIDAD (TAROTISTAS) ====================

@login_required
def calendario_disponibilidad_view(request):
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo tarotistas pueden acceder.')
        return redirect('home')

    tarotista = request.user.tarotista
    horarios = Disponibilidad.objects.filter(tarotista=tarotista)

    eventos = []
    for h in horarios:
        eventos.append({
            'id': h.id,
            'title': 'Reservado' if h.reservado else 'Disponible',
            'start': h.hora_inicio.isoformat(),
            'end': h.hora_fin.isoformat(),
            'extendedProps': {'is_reserved': h.reservado}
        })

    context = {
        'total_horarios': horarios.count(),
        'horarios_disponibles': horarios.filter(reservado=False).count(),
        'horarios_reservados': horarios.filter(reservado=True).count(),
        'horarios_eventos_json': json.dumps(eventos)
    }
    return render(request, 'calendario.html', context)


@require_POST
@login_required
@csrf_exempt
def manejar_disponibilidad_ajax(request):
    if not hasattr(request.user, 'tarotista'):
        return JsonResponse({'success': False, 'error': 'Permiso denegado'}, status=403)

    try:
        data = json.loads(request.body)
        action = data.get('action')
        tarotista = request.user.tarotista

        if action == 'add':
            start_dt = datetime.fromisoformat(data['start_time'])
            end_dt = datetime.fromisoformat(data['end_time'])
            dia_semana = int(data['dia_semana'])

            if end_dt <= start_dt:
                return JsonResponse({'success': False, 'error': 'Horario inválido'}, status=400)

            solapado = Disponibilidad.objects.filter(
                tarotista=tarotista,
                dia_semana=dia_semana,
                hora_inicio__lt=end_dt.time(),
                hora_fin__gt=start_dt.time()
            ).exists()

            if solapado:
                return JsonResponse({'success': False, 'error': 'Horario solapado'}, status=409)

            disp = Disponibilidad.objects.create(
                tarotista=tarotista,
                dia_semana=dia_semana,
                hora_inicio=start_dt.time(),
                hora_fin=end_dt.time(),
                reservado=False
            )

            return JsonResponse({'success': True, 'event_id': disp.id})

        elif action == 'delete':
            disp = Disponibilidad.objects.get(
                id=data['event_id'],
                tarotista=tarotista,
                reservado=False
            )
            disp.delete()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Acción inválida'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ==================== TOMA DE HORAS (CLIENTES) ====================

@login_required
def toma_de_horas(request):
    """
    Muestra horarios disponibles de TODAS las tarotistas
    """
    horarios = Disponibilidad.objects.filter(
        reservado=False,
        tarotista__disponible=True
    ).select_related('tarotista', 'tarotista__usuario')

    eventos = []
    for h in horarios:
        eventos.append({
            'id': h.id,
            'title': f"Disponible – {h.tarotista.usuario.first_name}",
            'start': h.hora_inicio.isoformat(),
            'end': h.hora_fin.isoformat(),
        })

    context = {
        'horarios_eventos_json': json.dumps(eventos)
    }
    return render(request, 'toma_de_horas.html', context)


@require_POST
@login_required
@csrf_exempt
def reservar_hora_ajax(request):
    try:
        data = json.loads(request.body)
        disp = Disponibilidad.objects.get(id=data['event_id'], reservado=False)

        disp.reservado = True
        disp.save()

        # (opcional) crear cita aquí más adelante

        return JsonResponse({'success': True})

    except Disponibilidad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Horario no disponible'}, status=404)

