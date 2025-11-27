# tarotistas/forms.py
from django import forms
from usuarios.models import Usuario
from .models import Tarotista

class TarotistaAdminForm(forms.ModelForm):
    # Campos del usuario que el admin puede completar
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    email = forms.EmailField(label='Correo electrónico')
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    
    class Meta:
        model = Tarotista
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 
                 'especialidad', 'experiencia', 'precio_por_sesion', 'descripcion']
    
    def save(self, commit=True):
        # Crear el usuario primero
        usuario_data = {
            'username': self.cleaned_data['username'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'email': self.cleaned_data['email'],
        }
        
        # Crear usuario con contraseña
        usuario = Usuario.objects.create_user(
            username=usuario_data['username'],
            email=usuario_data['email'],
            password=self.cleaned_data['password'],
            first_name=usuario_data['first_name'],
            last_name=usuario_data['last_name']
        )
        
        # Luego crear el tarotista
        tarotista = super().save(commit=False)
        tarotista.usuario = usuario
        
        if commit:
            tarotista.save()
        
        return tarotista