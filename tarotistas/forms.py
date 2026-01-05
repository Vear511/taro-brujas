# tarotistas/forms.py

from django import forms
from .models import Tarotista


class TarotistaForm(forms.ModelForm):
    class Meta:
        model = Tarotista
        fields = [
            "biografia",
            "experiencia",
            "especialidades",
            "tarifa",
            "foto_perfil",
            "disponible",
            "horario_inicio",
            "horario_fin",
        ]
        widgets = {
            "biografia": forms.Textarea(attrs={"rows": 4}),
            "experiencia": forms.Textarea(attrs={"rows": 3}),
            "especialidades": forms.Textarea(attrs={"rows": 3}),
        }
