from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "bloqueado",
        "es_tarotista",
        "email_verificado",
        "creado_en",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "bloqueado",
        "es_tarotista",
        "email_verificado",
    )

    search_fields = ("username", "email", "first_name", "last_name", "rut")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Campos extra",
            {
                "fields": (
                    "rut",
                    "telefono",
                    "fecha_nacimiento",
                    "apodo",
                    "bio",
                    "avatar",
                    "bloqueado",
                    "es_tarotista",
                    "email_verificado",
                )
            },
        ),
    )
