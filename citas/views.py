from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CitaForm
from tarotistas.models import Tarotista

@login_required
def mis_citas(request):
    return render(request, 'mis_citas.html')

@login_required
def agendar_cita(request):
    tarotistas = Tarotista.objects.filter(disponible=True)
    
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            # Procesar la cita aquí
            return render(request, 'cita_confirmada.html')
    else:
        form = CitaForm()
    
    context = {
        'tarotistas': tarotistas,
        'form': form,
        'servicio_seleccionado': None,
    }
    return render(request, 'agendar_cita.html', context)
#@login_required
#def detalle_cita(request, cita_id):
#    cita = get_object_or_404(Cita, id=cita_id, cliente=request.user)
#    return render(request, 'detalle_cita.html', {'cita': cita})
