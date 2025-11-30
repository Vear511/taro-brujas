from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Reporte
from citas.models import Cita
from usuarios.models import Usuario

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')


# ==================== VISTAS DE REPORTES ====================

@login_required
def reportes_lista(request):
    """Lista de reportes - solo los de la tarotista autenticada"""
    # Verificar que el usuario sea tarotista
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden acceder a esta sección.')
        return redirect('perfil')
    
    tarotista = request.user.tarotista
    reportes = Reporte.objects.filter(tarotista=tarotista)
    
    context = {
        'reportes': reportes,
        'reportes_recientes': reportes[:3],
    }
    return render(request, 'reportes.html', context)


@login_required
def crear_reporte(request):
    """Crear un nuevo reporte de paciente"""
    # Verificar que sea tarotista
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
            # renderizamos el formulario con context para preservar el estado
            citas = Cita.objects.filter(tarotista=tarotista, estado='completada')
            pacientes = Usuario.objects.filter(tarotista__isnull=True)
            return render(request, 'crear_reporte.html', {'citas': citas, 'pacientes': pacientes})
        
        try:
            paciente = get_object_or_404(Usuario, id=paciente_id)
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
    
    # Verificar que solo la tarotista que creó el reporte pueda verlo
    if reporte.tarotista.usuario != request.user:
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
    
    # Verificar que solo la tarotista que creó el reporte pueda editarlo
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
    
    # Verificar que solo la tarotista que creó el reporte pueda eliminarlo
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

import json
from django.shortcuts import render
from .models import Disponibilidad # Asume que tienes un modelo llamado Disponibilidad

def calendario_disponibilidad_view(request):
    # 1. Obtener los eventos del usuario
    horarios = Disponibilidad.objects.filter(usuario=request.user).all()
    
    # 2. Formatear para FullCalendar
    eventos_fc = []
    for horario in horarios:
        eventos_fc.append({
            'id': horario.pk, # Necesario para la eliminación
            'title': 'Reservado' if horario.reservado else 'Disponible',
            'start': horario.hora_inicio.isoformat(),
            'end': horario.hora_fin.isoformat(),
            'extendedProps': {
                'is_reserved': horario.reservado # Propiedad extra para lógica de clic
            }
        })

    # 3. Serializar a JSON
    horarios_eventos_json = json.dumps(eventos_fc)

    context = {
        # Variables para las tarjetas de resumen (debes calcularlas)
        'total_horarios': Disponibilidad.objects.filter(usuario=request.user).count(),
        'horarios_disponibles': Disponibilidad.objects.filter(usuario=request.user, reservado=False).count(),
        'horarios_reservados': Disponibilidad.objects.filter(usuario=request.user, reservado=True).count(),
        
        # La variable clave para el frontend
        'horarios_eventos_json': horarios_eventos_json 
    }
    return render(request, 'tu_app/calendario.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt # Se usa para simplificar en desarrollo, pero es mejor usar el token.
import json
from datetime import datetime
from .models import Disponibilidad

@require_POST
@csrf_exempt # Quita esto si puedes configurar correctamente el CSRF token en el frontend
def manejar_disponibilidad_ajax(request):
    try:
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'add':
            # Lógica para agregar un nuevo horario
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')

            # Convertir las cadenas de tiempo (YYYY-MM-DDTHH:MM) a objetos datetime
            start_dt = datetime.fromisoformat(start_time_str)
            end_dt = datetime.fromisoformat(end_time_str)

            # Crear el nuevo objeto de disponibilidad
            nueva_disponibilidad = Disponibilidad.objects.create(
                usuario=request.user, # Asume que el usuario está autenticado
                hora_inicio=start_dt,
                hora_fin=end_dt,
                reservado=False
            )
            return JsonResponse({'success': True, 'message': 'Horario añadido', 'event_id': nueva_disponibilidad.pk})

        elif action == 'delete':
            # Lógica para eliminar un horario existente
            event_id = data.get('event_id')
            horario = Disponibilidad.objects.get(pk=event_id, usuario=request.user, reservado=False)
            horario.delete()
            return JsonResponse({'success': True, 'message': 'Horario eliminado'})

        else:
            return JsonResponse({'success': False, 'error': 'Acción no válida'}, status=400)

    except Disponibilidad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Horario no encontrado o ya reservado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
