# usuarios/forms.py
from django import forms
from .models import Usuario
from .utils import validar_rut_detalle, validar_rut

class UsuarioForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = ['rut', 'telefono', 'fecha_nacimiento', 'bio', 'avatar', 'apodo']

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')

        if rut:
            valido, motivo = validar_rut_detalle(rut)
            if not valido:
                if motivo == 'format':
                    raise forms.ValidationError('Formato de RUT inválido. Use 12.345.678-5')
                elif motivo == 'dv':
                    raise forms.ValidationError('RUT no válido: dígito verificador incorrecto.')
                else:
                    raise forms.ValidationError('RUT inválido.')

        return rut
