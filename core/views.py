from datetime import datetime
import json 

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 

# Importaciones de Modelos
from .models import Reporte, Disponibilidad 
from django.db.models import Q
from citas.models import Cita
from usuarios.models import Usuario
# Asumimos que también tienes el modelo Tarotista disponible para request.user.tarotista

# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')

@login_required
def reportes_lista(request):
    """
    Lista de reportes con búsqueda y orden:
    - Tarotistas: muestran sus reportes.
    - Usuarios normales: muestran solo sus reportes.
    - Parámetros GET:
        - q: texto de búsqueda (username, first_name, last_name, experiencia)
        - order: 'asc' o 'desc' (por fecha_reporte). Default 'desc'.
    """

    q = request.GET.get('q', '').strip()
    order = request.GET.get('order', 'desc')

    # Base queryset según tipo de usuario
    if hasattr(request.user, 'tarotista'):
        tarotista = request.user.tarotista
        reportes = Reporte.objects.filter(tarotista=tarotista)
    else:
        reportes = Reporte.objects.filter(paciente=request.user)

    # Aplicar búsqueda
    try:
        if q:
            reportes = reportes.filter(
                Q(paciente__username__icontains=q) |
                Q(paciente__first_name__icontains=q) |
                Q(paciente__last_name__icontains=q) |
                Q(experiencia__icontains=q)
            )
    except Exception as e:
        # Mostrar mensaje al usuario
        messages.error(request, 'Ocurrió un error al realizar la búsqueda. Intenta con otro término.')
        # Mostrar error real en consola para depuración
        print("Error en búsqueda:", e)
        # Evitar romper la vista
        reportes = Reporte.objects.none()

    # Ordenamiento
    if order == 'asc':
        reportes = reportes.order_by('fecha_reporte')
    else:
        reportes = reportes.order_by('-fecha_reporte')

    # Detectar búsqueda sin resultados
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
    """Crear un nuevo reporte de paciente"""
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
            
            cita = None
            if cita_id:
                cita = get_object_or_404(Cita, id=cita_id)
            
            reporte = Reporte.objects.create(
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
    
    # GET: Obtener citas del tarotista para seleccionar
    citas = Cita.objects.filter(tarotista=tarotista, estado='completada')

    # Obtener todos los usuarios para el selector
    pacientes = Usuario.objects.all()

    context = {
        'citas': citas,
        'pacientes': pacientes,
    }
    return render(request, 'crear_reporte.html', context)


@login_required
def detalle_reporte(request, reporte_id):
    """Ver detalles de un reporte"""
    reporte = get_object_or_404(Reporte, id=reporte_id)
    
    # Si es tarotista, mantener la validación actual: solo la tarotista que creó el reporte puede verlo
    if hasattr(request.user, 'tarotista'):
        if reporte.tarotista.usuario != request.user:
            messages.error(request, 'No tienes permiso para ver este reporte.')
            return redirect('core:reportes')
    else:
        # Usuario normal: solo el paciente asociado puede ver su reporte
        if reporte.paciente != request.user:
            messages.error(request, 'No tienes permiso para ver este reporte.')
            return redirect('core:reportes')
    
    context = {
        'reporte': reporte,
    }
    return render(request, 'detalle_reporte.html', context)


@login_required
def editar_reporte(request, reporte_id):
    """Editar un reporte existente"""
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
    
    context = {
        'reporte': reporte,
    }
    return render(request, 'editar_reporte.html', context)


@login_required
def eliminar_reporte(request, reporte_id):
    """Eliminar un reporte"""
    reporte = get_object_or_404(Reporte, id=reporte_id)
    
    if reporte.tarotista.usuario != request.user:
        messages.error(request, 'No tienes permiso para eliminar este reporte.')
        return redirect('core:reportes')
    
    if request.method == 'POST':
        reporte.delete()
        messages.success(request, 'Reporte eliminado exitosamente.')
        return redirect('core:reportes')
    
    context = {
        'reporte': reporte,
    }
    return render(request, 'confirmar_eliminar_reporte.html', context)

# ==================== VISTAS DE DISPONIBILIDAD (CORREGIDAS Y ROBUSTAS) ====================

@login_required
def calendario_disponibilidad_view(request):
    """Muestra el calendario y la interfaz para gestionar la disponibilidad."""
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden gestionar su disponibilidad.')
        return redirect('perfil') 

    # CORREGIDO: Usar tarotista=request.user.tarotista
    horarios = Disponibilidad.objects.filter(tarotista=request.user.tarotista).all()
    
    # 2. Formatear para FullCalendar
    eventos_fc = []
    for horario in horarios:
        eventos_fc.append({
            'id': horario.pk, 
            'title': 'Reservado' if horario.reservado else 'Disponible',
            # Las fechas de inicio y fin son de tipo TimeField en models.py, 
            # pero la vista las recupera del objeto datetime completo
            # Usar .isoformat() para incluirlas en el JSON
            'start': horario.hora_inicio.isoformat(), 
            'end': horario.hora_fin.isoformat(),
            'extendedProps': {
                'is_reserved': horario.reservado 
            }
        })

    horarios_eventos_json = json.dumps(eventos_fc)

    # CORREGIDO: Usar tarotista=request.user.tarotista
    context = {
        'total_horarios': Disponibilidad.objects.filter(tarotista=request.user.tarotista).count(),
        'horarios_disponibles': Disponibilidad.objects.filter(tarotista=request.user.tarotista, reservado=False).count(),
        'horarios_reservados': Disponibilidad.objects.filter(tarotista=request.user.tarotista, reservado=True).count(),
        
        'horarios_eventos_json': horarios_eventos_json 
    }
    return render(request, 'calendario.html', context)


@require_POST
@login_required
@csrf_exempt 
def manejar_disponibilidad_ajax(request):
    """Maneja las peticiones AJAX para añadir o eliminar disponibilidad."""
    if not hasattr(request.user, 'tarotista'):
        return JsonResponse({'success': False, 'error': 'Permiso denegado.'}, status=403)
          
    try:
        data = json.loads(request.body)
        action = data.get('action')
        tarotista_obj = request.user.tarotista 

        if action == 'add':
            # Obtener datos de tiempo
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            dia_semana_val = data.get('dia_semana') 

            # Validar que dia_semana_val no sea None
            if dia_semana_val is None:
                return JsonResponse({'success': False, 'error': 'Falta el valor de dia_semana en la petición AJAX.'}, status=400)
            
            # Convertir a entero
            try:
                dia_semana_final = int(dia_semana_val) 
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'error': 'El dia_semana debe ser un número entero (0-6).'}, status=400)
            
            # Convertir las cadenas de tiempo a objetos datetime (sin segundos/microsegundos)
            start_dt = datetime.fromisoformat(start_time_str).replace(second=0, microsecond=0)
            end_dt = datetime.fromisoformat(end_time_str).replace(second=0, microsecond=0)

            # Validación de solapamiento SOLO dentro del mismo día de semana
            solapados = Disponibilidad.objects.filter(
                tarotista=tarotista_obj,
                dia_semana=dia_semana_final,
                hora_inicio__lt=end_dt,
                hora_fin__gt=start_dt
            )

            if solapados.exists():
                return JsonResponse({'success': False, 'error': 'El horario se solapa con uno existente.'}, status=409)

            # Crear el nuevo objeto de disponibilidad
            nueva_disponibilidad = Disponibilidad.objects.create(
                tarotista=tarotista_obj,
                dia_semana=dia_semana_final,
                hora_inicio=start_dt.time(),  # si tu modelo usa TimeField
                hora_fin=end_dt.time(),
                reservado=False
            )
            return JsonResponse({'success': True, 'message': 'Horario añadido', 'event_id': nueva_disponibilidad.pk})

        elif action == 'delete':
            event_id = data.get('event_id')
            horario = Disponibilidad.objects.get(pk=event_id, tarotista=tarotista_obj, reservado=False)
            horario.delete()
            return JsonResponse({'success': True, 'message': 'Horario eliminado'})

        else:
            return JsonResponse({'success': False, 'error': 'Acción no válida'}, status=400)

    except Disponibilidad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Horario no encontrado o ya reservado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno en el servidor: {str(e)}'}, status=500)
    
def toma_de_horas(request):
    # Aquí puedes pasar datos al template si lo necesitas
    return render(request, 'toma_de_horas.html')
