from django import forms
from .models import Cita
from tarotistas.models import Tarotista
from django.utils import timezone


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['tarotista', 'fecha_hora', 'notas']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'notas': forms.Textarea(attrs={'rows': 3})
        }
        labels = {
            'notas': 'Notas o preguntas específicas'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tarotista'].queryset = Tarotista.objects.filter(disponible=True)

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data['fecha_hora']
        if fecha_hora < timezone.now():
            raise forms.ValidationError("No puedes agendar una cita en el pasado.")
        return fecha_hora
