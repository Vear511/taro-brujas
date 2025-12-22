from django import forms
from .models import Cita
from tarotistas.models import Tarotista

class CitaForm(forms.Form):
    tarotista = forms.ModelChoiceField(
        queryset=Tarotista.objects.filter(disponible=False),
        empty_label="Selecciona un tarotista"
    )
    fecha = forms.DateField(widget=forms.SelectDateWidget)
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    notas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Notas o preguntas específicas'
    )
