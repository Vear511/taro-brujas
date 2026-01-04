from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'bloqueado',
        'creado_en',
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'bloqueado',
        'creado_en',
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': (
                'telefono',
                'fecha_nacimiento',
                'bio',
                'avatar',
                'bloqueado',
            )
        }),
    )
