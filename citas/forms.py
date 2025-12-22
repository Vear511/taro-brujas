from django import forms
from tarotistas.models import Tarotista

class CitaForm(forms.Form):
    tarotista = forms.ModelChoiceField(
        queryset=Tarotista.objects.none(),
        empty_label="Selecciona un tarotista"
    )
    fecha = forms.DateField(widget=forms.SelectDateWidget)
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    notas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Notas o preguntas específicas'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tarotista'].queryset = (
            Tarotista.objects
            .select_related('usuario')
            .filter(disponible=True)
            .order_by('usuario__first_name')
        )
