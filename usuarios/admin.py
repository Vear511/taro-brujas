from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que existen en AbstractUser + tus extras actuales
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "es_tarotista",
        "email_verificado",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "es_tarotista",
        "email_verificado",
    )

    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    # Agrega tus campos extra al formulario del admin
    fieldsets = UserAdmin.fieldsets + (
        ("Campos extra", {"fields": ("avatar", "es_tarotista", "email_verificado")}),
    )
