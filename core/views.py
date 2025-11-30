from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Reporte
from citas.models import Cita
from usuarios.models import Usuario

# ==================== VISTAS BÁSICAS ====================

def home(request):
    return render(request, 'home.html')

def servicios(request):
    return render(request, 'servicios.html')

def sobre_nosotras(request):
    return render(request, 'sobre_nosotras.html')

# --------------------------------------------------------
# ==================== VISTAS DE REPORTES ====================

@login_required
def reportes_lista(request):
    """Lista de reportes - solo los de la tarotista autenticada"""
    # 1. Verificar que el usuario sea tarotista
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden acceder a esta sección.')
        return redirect('perfil')
    
    tarotista = request.user.tarotista
    # Se añade .select_related() para optimizar las consultas a la DB
    reportes = Reporte.objects.filter(tarotista=tarotista).select_related('paciente', 'cita')
    
    context = {
        'reportes': reportes,
        # Se usa list() o QuerySet slicing para evitar evaluar dos veces el QuerySet completo
        'reportes_recientes': reportes[:3],
    }
    return render(request, 'reportes.html', context)


@login_required
def crear_reporte(request):
    """Crear un nuevo reporte de paciente"""
    # 1. Verificar que sea tarotista
    if not hasattr(request.user, 'tarotista'):
        messages.error(request, 'Solo los tarotistas pueden crear reportes.')
        return redirect('perfil')
    
    tarotista = request.user.tarotista
    
    # Pre-cargamos los datos necesarios para el formulario, tanto para GET como para POST fallido
    citas_completadas = Cita.objects.filter(tarotista=tarotista, estado='completada')
    # Se obtienen todos los usuarios, pero se filtra para excluir a los que tienen perfil de tarotista
    pacientes_activos = Usuario.objects.filter(tarotista__isnull=True) 

    if request.method == 'POST':
        # 2. Obtener datos del POST y definir 'experiencia'
        paciente_id = request.POST.get('paciente_id')
        cita_id = request.POST.get('cita_id')
        experiencia_post = request.POST.get('experiencia') # Nuevo nombre para evitar conflicto
        contenido_post = request.POST.get('contenido') # Asumiendo que hay otro campo de contenido

        # 3. Validación de campos requeridos
        if not paciente_id or not experiencia_post:
            messages.error(request, 'Por favor, selecciona un paciente y completa el campo de experiencia.')
            context = {
                'citas': citas_completadas,
                'pacientes': pacientes_activos,
                'experiencia_previa': experiencia_post, # Pasar datos para que no se pierdan
                'contenido_previo': contenido_post,
            }
            return render(request, 'crear_reporte.html', context)
        
        try:
            # 4. Corregido: Buscar paciente (una sola vez)
            paciente = get_object_or_404(Usuario, id=paciente_id)
            
            cita = None
            if cita_id:
                cita = get_object_or_404(Cita, id=cita_id)
            
            # 5. Corregido: Crear el reporte pasando todos los campos
            reporte = Reporte.objects.create(
                tarotista=tarotista,
                paciente=paciente,
                cita=cita,
                experiencia=experiencia_post, # Se añaden los campos de contenido
                # contenido=contenido_post, # Descomentar si existe este campo
            )
            
            messages.success(request, 'Reporte creado exitosamente.')
            return redirect('core:reportes')
            
        except Http404:
            messages.error(request, 'Paciente o Cita no encontrado.')
            return redirect('core:crear_reporte')
        except Exception as e:
            # Captura de errores de base de datos o lógicos
            messages.error(request, f'Error al crear el reporte: {str(e)}')
            return redirect('core:crear_reporte')
    
    # GET: Renderizar el formulario con los datos pre-cargados
    context = {
        'citas': citas_completadas,
        'pacientes': pacientes_activos,
    }
    return render(request, 'crear_reporte.html', context)


@login_required
def detalle_reporte(request, reporte_id):
    """Ver detalles de un reporte"""
    # Se usa select_related para obtener la información de tarotista y usuario en una sola consulta
    reporte = get_object_or_404(Reporte.objects.select_related('tarotista__usuario'), id=reporte_id)
    
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
            # 6. Mejorado: Usar .get() con un valor por defecto seguro
            reporte.experiencia = request.POST.get('experiencia', reporte.experiencia)
            
            # Asumiendo que 'contenido' también se puede editar
            # reporte.contenido = request.POST.get('contenido', reporte.contenido) 
            
            estado = request.POST.get('estado')
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
