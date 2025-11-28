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

# En tu archivo views.py

# Asegúrate de importar tus modelos
from django.shortcuts import render
from .models import Tarotista # Tu modelo para tarotistas_tarotista

def sobre_nosotras_view(request):
    """
    Obtiene todos los perfiles de tarotistas y, en una sola consulta,
    obtiene los datos del usuario relacionado (JOIN implícito).
    """
    
    # 1. Consulta eficiente: 
    # select_related('user') realiza un JOIN para obtener los datos de usuarios_usuario
    # junto con los de tarotistas_tarotista en una sola consulta.
    perfiles_tarotistas = Tarotista.objects.select_related('user').all()
    
    # 2. Formatear los datos para la plantilla
    tarotistas_data = []
    
    for perfil in perfiles_tarotistas:
        # 'perfil' es el registro de tarotistas_tarotista
        # 'perfil.user' es el registro de usuarios_usuario
        user = perfil.user 

        # Asegúrate de que el usuario esté activo y no sea un administrador/staff si es necesario
        if not user.is_active:
             continue 

        tarotistas_data.append({
            # Datos del modelo usuarios_usuario (Columnas 1, 5, 6, 7, 8, 15, 17)
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'avatar': user.avatar.url if user.avatar else '/static/default/path.jpg', # Manejo de imágenes
            'rut': user.rut, # Asumiendo que es un campo del modelo User
            
            # Datos de la tabla tarotistas_tarotista (ej: la bio, la especialidad, etc.)
            'bio': perfil.bio, # Asumiendo que 'bio' es el campo de descripción en el perfil
            'especialidad': perfil.especialidad if hasattr(perfil, 'especialidad') else None,
        })
        
    context = {
        'tarotistas': tarotistas_data # Esta es la lista que se pasa a la plantilla
    }
    
    return render(request, 'about_us.html', context)
