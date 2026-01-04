from django import forms
from usuarios.models import Usuario
from .models import Tarotista


class TarotistaAdminForm(forms.ModelForm):
    # Campos del Usuario
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    email = forms.EmailField(label='Correo electrónico')
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Contraseña',
        help_text='Debe ser segura y no reutilizada'
    )

    class Meta:
        model = Tarotista
        fields = ['descripcion', 'disponible']

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def save(self, commit=True):
        # Crear el usuario asociado
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )

        # Crear el tarotista
        tarotista = super().save(commit=False)
        tarotista.usuario = usuario

        if commit:
            tarotista.save()

        return tarotista
    from django import forms
from usuarios.models import Usuario
from .models import Tarotista

class TarotistaAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    email = forms.EmailField(label='Correo electrónico')
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

    class Meta:
        model = Tarotista
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password',
            'descripcion',
            'disponible'
        ]

    def save(self, commit=True):
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )

        tarotista = super().save(commit=False)
        tarotista.usuario = usuario

        if commit:
            tarotista.save()

        return tarotista

