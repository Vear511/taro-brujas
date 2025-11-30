from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que aparecen en la lista de la tabla de administración
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'creado_en',
        # === AÑADIDO: Muestra el estado de baneo en la lista ===
        'ban', 
    )
    
    # Filtros que aparecen en la barra lateral derecha
    list_filter = (
        'is_staff', 
        'is_superuser', 
        'creado_en',
        # === AÑADIDO: Permite filtrar por estado de baneo ===
        'ban', 
    )
    
    # Define la estructura y el contenido del formulario de edición de usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional (Brujitas)', {
            # === AÑADIDOS: rut, apodo, y el campo de baneo ===
            'fields': (
                'rut',
                'telefono', 
                'fecha_nacimiento', 
                'bio', 
                'avatar',
                'apodo',
                'ban'
            )
        }),
    )
