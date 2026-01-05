from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Tarotista

User = get_user_model()


def es_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(es_admin)
def lista_tarotistas(request):
    tarotistas = Tarotista.objects.select_related("usuario").all()
    return render(request, "lista_tarotistas.html", {"tarotistas": tarotistas})


@login_required
@user_passes_test(es_admin)
def agregar_tarotista(request):
    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        especialidad = request.POST.get("especialidad", "")
        descripcion = request.POST.get("descripcion", "")

        usuario = get_object_or_404(User, id=usuario_id)

        if hasattr(usuario, "tarotista"):
            messages.error(request, "Este usuario ya es tarotista.")
            return redirect("tarotistas:lista_tarotistas")

        Tarotista.objects.create(
            usuario=usuario,
            especialidad=especialidad,
            descripcion=descripcion,
        )

        # ✅ clave: asegurar bandera para templates/roles
        if not getattr(usuario, "es_tarotista", False):
            usuario.es_tarotista = True
            usuario.save(update_fields=["es_tarotista"])

        messages.success(request, "Tarotista agregado correctamente.")
        return redirect("tarotistas:lista_tarotistas")

    usuarios = User.objects.all()
    return render(request, "agregar_tarotista.html", {"usuarios": usuarios})


@login_required
@user_passes_test(es_admin)
def bloquear_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)

    # ✅ usar is_active (estándar Django) para bloquear login
    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])

    estado = "bloqueado" if not usuario.is_active else "desbloqueado"
    messages.success(request, f"Usuario {estado} correctamente.")
    return redirect("tarotistas:lista_tarotistas")

