from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CitaForm

@login_required
def mis_citas(request):
    return render(request, 'mis_citas.html')

@login_required
def agendar_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            # Aquí luego guardarás la cita
            return render(request, 'cita_confirmada.html')
    else:
        form = CitaForm()

    context = {
        'form': form,
        'servicio_seleccionado': None,
    }
    return render(request, 'agendar_cita.html', context)
