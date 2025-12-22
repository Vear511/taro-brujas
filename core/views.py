from datetime import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Importaciones de Modelos
# NOTA: Los modelos Reporte y Disponibilidad se asumen locales a esta aplicación,
# o se configuran en el settings.py para ser resueltos correctamente.
from .models import Reporte, Disponibilidad
from citas.models import Cita
from usuarios.models import Usuario

# *** IMPORTACIÓN ADICIONAL NECESARIA ***
# Se asume que el modelo Tarotista reside en la aplicación 'tarotistas'
try:
    from .models import Tarotista # Cambio: asumo que Tarotista está en el mismo .models
except ImportError:
    # Manejo de error si la app 'tarotistas' no existe o no tiene el modelo
    class Tarotista: # Define un placeholder si no existe
        pass
# **************************************


# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    """
    Vista que recupera los datos combinados (Usuario + Tarotista) para
    la sección pública 'Conoce a nuestras tarotistas', garantizando valores de respaldo.

    Utiliza select_related('usuario') para realizar el INNER JOIN entre Tarotista y Usuario.
    """
    
    # Suponiendo que el modelo Tarotista ya está correctamente importado arriba.
    if 'Tarotista' in globals() and isinstance(Tarotista, type):
        
        # Consulta para traer todos los registros de diagnóstico
        tarotistas_data = Tarotista.objects.select_related('usuario').all()
        
        tarotistas_listos = []
        
        for t in tarotistas_data:
            try:
                # ----------------------------------------------------
                # GARANTIZAR VALORES DE RESPALDO (FALLBACK)
                # ----------------------------------------------------
                
                # 1. Nombre de Respaldo: Prioriza first_name, luego username, luego un valor por defecto.
                nombre_a_mostrar = t.usuario.first_name or t.usuario.username or "Tarotista (Nombre Pendiente)"
                
                # 2. Descripción de Respaldo: Usa la descripción o un mensaje por defecto.
                descripcion_a_mostrar = t.descripcion or "Esta tarotista aún no ha completado su biografía, pero está lista para leer tus cartas."
                
                # 3. Imagen de Respaldo: Ya implementado. Usa la imagen del avatar o una por defecto.
                url_imagen_a_mostrar = t.usuario.avatar.url if t.usuario.avatar else '/static/img/placeholder_default.png'
                
                # ----------------------------------------------------
                
                tarotistas_listos.append({
                    'nombre': nombre_a_mostrar, 
                    'descripcion': descripcion_a_mostrar, 
                    'url_imagen': url_imagen_a_mostrar, 
                })
            
            except AttributeError:
                # Este bloque se mantiene para saltar registros si el usuario_id está roto
                print(f"ERROR DE BD: El registro de Tarotista (ID: {getattr(t, 'id', 'N/A')}) no tiene un usuario válido asociado.")
                continue
            
        context = {
            'tarotistas': tarotistas_listos
        }
    
    else:
        # Si el modelo Tarotista no se pudo importar (lo que indica un error de arquitectura),
        # se pasa una lista vacía para evitar fallos.
        context = {
            'tarotistas': [] 
        }

    return render(request, 'sobre_nosotras.html', context)

# --- VISTAS DE REPORTES ---

@login_required
def reportes_lista(request):
    """Lista de reportes - solo los de la tarotista autenticada"""
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

            # 1. Validar que dia_semana_val no sea None (evita el error NOT NULL)
            if dia_semana_val is None:
                return JsonResponse({'success': False, 'error': 'Falta el valor de dia_semana en la petición AJAX.'}, status=400)
            
            # 2. Convertir y validar que el valor es un entero (ROBUSTEZ)
            try:
                # Usamos int() para garantizar que el valor sea un entero
                dia_semana_final = int(dia_semana_val) 
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'error': 'El dia_semana debe ser un número entero (0-6).'}, status=400)
            
            # Convertir las cadenas de tiempo (YYYY-MM-DDTHH:MM) a objetos datetime
            start_dt = datetime.fromisoformat(start_time_str)
            end_dt = datetime.fromisoformat(end_time_str)
            
            # Validación simple de solapamiento
            if Disponibilidad.objects.filter(
                tarotista=tarotista_obj, 
                hora_inicio__lt=end_dt, 
                hora_fin__gt=start_dt
            ).exists():
                return JsonResponse({'success': False, 'error': 'El horario se solapa con uno existente.'}, status=409)

            # Crear el nuevo objeto de disponibilidad
            nueva_disponibilidad = Disponibilidad.objects.create(
                tarotista=tarotista_obj,
                dia_semana=dia_semana_final, # <-- USAMOS EL VALOR CONVERTIDO Y SEGURO
                hora_inicio=start_dt,
                hora_fin=end_dt,
                reservado=False
            )
            return JsonResponse({'success': True, 'message': 'Horario añadido', 'event_id': nueva_disponibilidad.pk})

        elif action == 'delete':
            # Lógica para eliminar un horario existente
            event_id = data.get('event_id')
            horario = Disponibilidad.objects.get(pk=event_id, tarotista=tarotista_obj, reservado=False)
            horario.delete()
            return JsonResponse({'success': True, 'message': 'Horario eliminado'})

        else:
            return JsonResponse({'success': False, 'error': 'Acción no válida'}, status=400)

    except Disponibilidad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Horario no encontrado o ya reservado.'}, status=404)
    except Exception as e:
        # Esto atrapará errores como el formato ISO incorrecto de la fecha o JSON inválido
        return JsonResponse({'success': False, 'error': f'Error interno en el servidor: {str(e)}'}, status=500)
