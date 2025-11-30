import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
# Importamos csrf_exempt, aunque se recomienda usar el token CSRF estándar
from django.views.decorators.csrf import csrf_exempt 

# Importaciones de Modelos (Asegúrate de que 'Disponibilidad' esté disponible)
from .models import Reporte, Disponibilidad # Suponiendo que Disponibilidad está en .models
from citas.models import Cita
from usuarios.models import Usuario

# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')

# ... (Las VISTAS DE REPORTES están correctas y se mantienen iguales) ...
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
            # Aquí tienes una línea duplicada, la he dejado para que la revises:
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

---

# ==================== VISTAS DE DISPONIBILIDAD ====================

@login_required # <--- NECESARIO para que request.user funcione
def calendario_disponibilidad_view(request):
    """Muestra el calendario y la interfaz para gestionar la disponibilidad."""
    # Opcional: Verificar que el usuario sea tarotista si solo ellas pueden gestionarlo
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden gestionar su disponibilidad.')
        return redirect('perfil') 

    # 1. Obtener los eventos del usuario
    horarios = Disponibilidad.objects.filter(usuario=request.user).all()
    
    # 2. Formatear para FullCalendar
    eventos_fc = []
    for horario in horarios:
        eventos_fc.append({
            'id': horario.pk, 
            'title': 'Reservado' if horario.reservado else 'Disponible',
            'start': horario.hora_inicio.isoformat(),
            'end': horario.hora_fin.isoformat(),
            'extendedProps': {
                'is_reserved': horario.reservado 
            }
        })

    # 3. Serializar a JSON
    horarios_eventos_json = json.dumps(eventos_fc)

    context = {
        # Variables para las tarjetas de resumen
        'total_horarios': Disponibilidad.objects.filter(usuario=request.user).count(),
        'horarios_disponibles': Disponibilidad.objects.filter(usuario=request.user, reservado=False).count(),
        'horarios_reservados': Disponibilidad.objects.filter(usuario=request.user, reservado=True).count(),
        
        # La variable clave para el frontend
        'horarios_eventos_json': horarios_eventos_json 
    }
    # Corregir la ruta de la plantilla si es necesario
    return render(request, 'calendario.html', context) # <--- Revisar el nombre de tu plantilla


@require_POST
@login_required # <--- NECESARIO para autenticar request.user
@csrf_exempt # Mantenemos esto porque el frontend usa AJAX sin Forms de Django
def manejar_disponibilidad_ajax(request):
    """Maneja las peticiones AJAX para añadir o eliminar disponibilidad."""
    # Opcional: Verificar que el usuario sea tarotista
    if not hasattr(request.user, 'tarotista'):
         return JsonResponse({'success': False, 'error': 'Permiso denegado.'}, status=403)
         
    try:
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'add':
            # Lógica para agregar un nuevo horario
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')

            # Convertir las cadenas de tiempo (YYYY-MM-DDTHH:MM) a objetos datetime
            # Esto maneja los minutos perfectamente
            start_dt = datetime.fromisoformat(start_time_str)
            end_dt = datetime.fromisoformat(end_time_str)
            
            # Validación simple de solapamiento (OPCIONAL pero RECOMENDADO)
            if Disponibilidad.objects.filter(
                usuario=request.user, 
                hora_inicio__lt=end_dt, 
                hora_fin__gt=start_dt
            ).exists():
                return JsonResponse({'success': False, 'error': 'El horario se solapa con uno existente.'}, status=409)

            # Crear el nuevo objeto de disponibilidad
            nueva_disponibilidad = Disponibilidad.objects.create(
                usuario=request.user, 
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
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'}, status=500)
