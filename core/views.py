from datetime import datetime, timedelta
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone as dj_timezone

from .models import Reporte, Disponibilidad
from citas.models import Cita
from usuarios.models import Usuario
from tarotistas.models import Tarotista


# --- Endpoint para reservar horario y crear cita ---
@csrf_exempt
@require_POST
@login_required
def reservar_horario(request):
    # Restringir a tarotistas
    if hasattr(request.user, 'es_tarotista') and request.user.es_tarotista:
        return JsonResponse(
            {'success': False, 'error': 'Los tarotistas no pueden agendar horas como clientes.'},
            status=403
        )

    try:
        data = json.loads(request.body)
        evento_id = data.get('evento_id')
        servicio = data.get('servicio', 'basico')

        if not evento_id:
            return JsonResponse({'success': False, 'error': 'ID de evento requerido.'}, status=400)

        # ⚠️ IMPORTANTE:
        # select_for_update() DEBE ejecutarse dentro de una transacción (PostgreSQL/Railway).
        with transaction.atomic():
            # Buscar el bloque de disponibilidad con lock
            bloque = Disponibilidad.objects.select_for_update().get(id=evento_id)

            if bloque.reservado:
                return JsonResponse({'success': False, 'error': 'El horario ya está reservado.'}, status=409)

            # Marcar como reservado
            bloque.reservado = True
            bloque.save()

            tarotista = bloque.tarotista

            # Calcular fecha y hora exacta
            today = timezone.now().date()
            js_today = (today.weekday() + 1) % 7
            dias_hasta = (bloque.dia_semana - js_today) % 7
            fecha = today + timedelta(days=dias_hasta)

            fecha_hora = datetime.combine(fecha, bloque.hora_inicio)

            cita = Cita.objects.create(
                cliente=request.user,
                tarotista=tarotista,
                fecha_hora=fecha_hora,
                duracion=(datetime.combine(fecha, bloque.hora_fin) - fecha_hora).seconds // 60,
                estado='confirmada',
                servicio=servicio
            )

            # Enviar correos de confirmación (esto usa tu EMAIL_BACKEND global SendGrid)
            tarotista_nombre = tarotista.usuario.get_full_name() if hasattr(tarotista, 'usuario') else str(tarotista)

            fecha_hora_aware = cita.fecha_hora
            if dj_timezone.is_naive(fecha_hora_aware):
                fecha_hora_aware = dj_timezone.make_aware(fecha_hora_aware, dj_timezone.get_current_timezone())

            fecha_str = fecha_hora_aware.strftime('%d/%m/%Y %H:%M')
            servicio_display = dict(Cita.SERVICIOS).get(servicio, servicio)
            subject = 'Confirmación de reserva de cita'

            # Correo para el usuario (solo si tiene email)
            if getattr(request.user, "email", None):
                message_usuario = (
                    f"Hola {request.user.get_full_name() or request.user.username},\n\n"
                    f"Tu cita ha sido reservada con éxito.\n\n"
                    f"Tarotista: {tarotista_nombre}\n"
                    f"Fecha y hora: {fecha_str}\n"
                    f"Tipo de servicio: {servicio_display}\n\n"
                    f"Gracias por confiar en Brujitas."
                )
                send_mail(subject, message_usuario, settings.DEFAULT_FROM_EMAIL, [request.user.email])

            # Correo para el tarotista (solo si tiene email)
            if hasattr(tarotista, 'usuario') and getattr(tarotista.usuario, "email", None):
                message_tarotista = (
                    f"Hola {tarotista_nombre},\n\n"
                    f"Tienes una nueva cita agendada.\n\n"
                    f"Cliente: {request.user.get_full_name() or request.user.username}\n"
                    f"Fecha y hora: {fecha_str}\n"
                    f"Tipo de servicio: {servicio_display}\n\n"
                    f"Por favor revisa tu panel para más detalles."
                )
                send_mail(subject, message_tarotista, settings.DEFAULT_FROM_EMAIL, [tarotista.usuario.email])

        return JsonResponse({'success': True, 'cita_id': cita.id})

    except Disponibilidad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Horario no encontrado.'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')


def servicios(request):
    return render(request, 'servicios.html')


def sobre_nosotras(request):
    # Mostrar tarotistas disponibles en la página "Sobre Nosotras"
    tarotistas = Tarotista.objects.filter(disponible=True).select_related('usuario')
    return render(request, 'sobre_nosotras.html', {'tarotistas': tarotistas})


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
        'search_no_results': bool(q) and not reportes.exists()
    }
    return render(request, 'reportes.html', context)


@login_required
def crear_reporte(request):
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden crear reportes.')
        return redirect('core:reportes')

    tarotista = request.user.tarotista

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        experiencia = request.POST.get('experiencia')
        cita_id = request.POST.get('cita_id')

        if not paciente_id or not experiencia:
            messages.error(request, 'Completa los campos obligatorios.')
            return redirect('core:crear_reporte')

        paciente = get_object_or_404(Usuario, id=paciente_id)
        cita = Cita.objects.filter(id=cita_id).first() if cita_id else None

        Reporte.objects.create(
            tarotista=tarotista,
            paciente=paciente,
            cita=cita,
            experiencia=experiencia
        )

        messages.success(request, 'Reporte creado correctamente.')
        return redirect('core:reportes')

    context = {
        'citas': Cita.objects.filter(tarotista=tarotista, estado='completada'),
        'pacientes': Usuario.objects.all()
    }
    return render(request, 'crear_reporte.html', context)


@login_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)

    if hasattr(request.user, 'tarotista'):
        if reporte.tarotista.usuario != request.user:
            messages.error(request, 'Acceso denegado.')
            return redirect('core:reportes')
    else:
        if reporte.paciente != request.user:
            messages.error(request, 'Acceso denegado.')
            return redirect('core:reportes')

    return render(request, 'detalle_reporte.html', {'reporte': reporte})


@login_required
def editar_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)

    if reporte.tarotista.usuario != request.user:
        messages.error(request, 'No tienes permisos.')
        return redirect('core:reportes')

    if request.method == 'POST':
        reporte.experiencia = request.POST.get('experiencia', reporte.experiencia)
        estado = request.POST.get('estado')
        if estado in ['abierto', 'cerrado']:
            reporte.estado = estado
        reporte.save()
        messages.success(request, 'Reporte actualizado.')
        return redirect('core:detalle_reporte', reporte_id=reporte.id)

    return render(request, 'editar_reporte.html', {'reporte': reporte})


@login_required
def eliminar_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)

    if reporte.tarotista.usuario != request.user:
        messages.error(request, 'No tienes permisos.')
        return redirect('core:reportes')

    if request.method == 'POST':
        reporte.delete()
        messages.success(request, 'Reporte eliminado.')
        return redirect('core:reportes')

    return render(request, 'confirmar_eliminar_reporte.html', {'reporte': reporte})


# ==================== DISPONIBILIDAD ====================

@login_required
def calendario_disponibilidad_view(request):
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo tarotistas.')
        return redirect('home')

    horarios = Disponibilidad.objects.filter(tarotista=request.user.tarotista)
    today = timezone.now().date()
    eventos = []

    # JS getDay(): 0=Sunday .. 6=Saturday
    # Python weekday(): 0=Monday .. 6=Sunday
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
            'color': '#dc3545' if h.reservado else '#28a745',
            'is_reserved': h.reservado
        })

    has_tarotista = hasattr(request.user, 'tarotista')
    tarotista_id = request.user.tarotista.id if has_tarotista else None

    context = {
        'horarios_eventos_json': json.dumps(eventos),
        'total_horarios': horarios.count(),
        'horarios_disponibles': horarios.filter(reservado=False).count(),
        'horarios_reservados': horarios.filter(reservado=True).count(),
        'debug_has_tarotista': has_tarotista,
        'debug_tarotista_id': tarotista_id,
    }
    return render(request, 'calendario.html', context)


@require_POST
@login_required
def manejar_disponibilidad_ajax(request):
    if not hasattr(request.user, 'tarotista'):
        return JsonResponse({'success': False}, status=403)

    data = json.loads(request.body)
    tarotista = request.user.tarotista

    if data.get('action') == 'add':
        dia = int(data['dia_semana'])
        start_dt = datetime.fromisoformat(data['start_time'])

        blocks = int(data.get('blocks', 1))

        existing_ids = []
        block_objs = []

        for i in range(blocks):
            b_start = start_dt + timedelta(minutes=30 * i)
            b_end = b_start + timedelta(minutes=30)

            exact = Disponibilidad.objects.filter(
                tarotista=tarotista,
                dia_semana=dia,
                hora_inicio=b_start.time(),
                hora_fin=b_end.time()
            ).first()

            if exact:
                existing_ids.append(exact.id)
                continue

            solapado = Disponibilidad.objects.filter(
                tarotista=tarotista,
                dia_semana=dia,
                hora_inicio__lt=b_end.time(),
                hora_fin__gt=b_start.time()
            ).exists()

            if solapado:
                return JsonResponse({'success': False, 'error': 'Horario solapado en alguno de los bloques'}, status=409)

            block_objs.append(Disponibilidad(
                tarotista=tarotista,
                dia_semana=dia,
                hora_inicio=b_start.time(),
                hora_fin=b_end.time()
            ))

        created = []
        if block_objs:
            created = Disponibilidad.objects.bulk_create(block_objs)

        all_blocks = [c.id for c in created]
        all_blocks.extend(existing_ids)

        events = []
        today = timezone.now().date()
        js_today = (today.weekday() + 1) % 7

        for bid in all_blocks:
            try:
                b = Disponibilidad.objects.get(id=bid)
            except Disponibilidad.DoesNotExist:
                continue

            dias_hasta = (b.dia_semana - js_today) % 7
            fecha = today + timedelta(days=dias_hasta)

            start_dt_block = datetime.combine(fecha, b.hora_inicio)
            end_dt_block = datetime.combine(fecha, b.hora_fin)

            events.append({
                'id': b.id,
                'start': start_dt_block.isoformat(),
                'end': end_dt_block.isoformat(),
                'title': 'Ocupado' if b.reservado else 'Disponible',
                'color': '#dc3545' if b.reservado else '#28a745',
                'is_reserved': b.reservado
            })

        return JsonResponse({'success': True, 'events': events})

    if data.get('action') == 'delete':
        Disponibilidad.objects.get(
            id=data['event_id'],
            tarotista=tarotista,
            reservado=False
        ).delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


@require_GET
def horarios_disponibles_json(request):
    eventos = []
    today = timezone.now().date()
    js_today = (today.weekday() + 1) % 7
    user = request.user
    es_tarotista = hasattr(user, 'tarotista')

    libres = Disponibilidad.objects.filter(reservado=False)
    for h in libres:
        dias_hasta = (h.dia_semana - js_today) % 7
        fecha = today + timedelta(days=dias_hasta)
        start_dt = datetime.combine(fecha, h.hora_inicio)
        end_dt = datetime.combine(fecha, h.hora_fin)
        eventos.append({
            'id': h.id,
            'title': 'Disponible',
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'is_reserved': False
            palette = [
                '#4e79a7',  # azul
                '#f28e2b',  # naranjo
                '#59a14f',  # verde
                '#b07aa1',  # morado
                '#76b7b2',  # turquesa
                '#edc948',  # amarillo
                '#e15759',  # rojo suave
                '#9c755f',  # café
                '#bab0ac',  # gris
        })

    reservados = Disponibilidad.objects.filter(reservado=True)
    for h in reservados:
        mostrar = False

        cita = Cita.objects.filter(
            tarotista=h.tarotista,
            fecha_hora__date=today + timedelta(days=(h.dia_semana - js_today) % 7),
            fecha_hora__time=h.hora_inicio
        ).first()

        if cita:
            if user.is_authenticated and cita.cliente_id == user.id:
                mostrar = True
            if es_tarotista and h.tarotista_id == user.tarotista.id:
                mostrar = True

        if mostrar:
            dias_hasta = (h.dia_semana - js_today) % 7
            fecha = today + timedelta(days=dias_hasta)
            start_dt = datetime.combine(fecha, h.hora_inicio)
            end_dt = datetime.combine(fecha, h.hora_fin)
            eventos.append({
                'id': h.id,
                'title': 'Ocupado',
                'start': start_dt.isoformat(),
                'end': end_dt.isoformat(),
                'color': '#dc3545',
                'is_reserved': True
            })

    return JsonResponse(eventos, safe=False)
def color_tarotista(tarotista_id: int) -> str:
        if not tarotista_id:
            return '#28a745'
        return palette[int(tarotista_id) % len(palette)]

def toma_de_horas(request):
    return render(request, 'toma_de_horas.html')
