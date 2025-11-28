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

# Importa tu modelo de Tarotista (asumiendo que se llama Tarotista en tu app)
from .models import Tarotista 
# Asumiendo que el modelo User está relacionado a Tarotista
from django.contrib.auth import get_user_model
User = get_user_model() 

def obtener_tarotistas_para_mostrar(request):
    """
    Función que consulta la BD para obtener todos los usuarios 
    que están registrados como tarotistas.
    """
    # Paso 1: Usar un filtro de existencia (lookup __isnull=False) o 
    # usar un método de consulta para hacer un JOIN implícito.
    # Esto filtra la tabla User para que SOLO se incluyan aquellos 
    # que tienen un registro relacionado en la tabla Tarotista.
    
    # Opción 1 (Asumiendo que User tiene un 'tarotista_profile' relacionado)
    # Lista de objetos User (que son Tarotistas)
    tarotistas_queryset = User.objects.filter(tarotista__isnull=False).order_by('id')
    
    # Opción 2 (Si Tarotista hereda de User o es OneToOneField)
    # tarotistas_queryset = Tarotista.objects.select_related('user').all()
    
    
    # Paso 2: Extraer solo los campos que necesitas
    # Usaremos .values() para obtener una lista de diccionarios, 
    # simulando el formato de salida para la plantilla.
    datos_tarotistas = tarotistas_queryset.values(
        'id',             # 1
        'username',       # 5
        'first_name',     # 6
        'last_name',      # 7
        'email',          # 8
        'rut',            # 17 (Asumiendo que 'rut' es un campo custom en User)
        'avatar'          # 15
    )
    
    # Si Tarotista tiene campos de bio o especialidad, necesitarías hacer un .select_related
    # y extraer esos campos también.
    
    # Paso 3: Renderizar la plantilla
    context = {
        'tarotistas': list(datos_tarotistas) # Pasamos la lista de diccionarios a la plantilla
    }
    
    return render_template('about_us.html', **context)
