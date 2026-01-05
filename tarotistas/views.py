# tarotistas/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from citas.models import Cita
from usuarios.models import Usuario
from .forms import TarotistaForm
from .models import Tarotista


def _es_admin(user: Usuario) -> bool:
    return user.is_staff or user.is_superuser


def _es_tarotista(user: Usuario) -> bool:
    return getattr(user, "es_tarotista", False) and hasattr(user, "tarotista")


# -------------------------------------------------------------------
# LISTADO DE TAROTISTAS (para administración)
# -------------------------------------------------------------------
@login_required
@user_passes_test(_es_admin)
def lista_tarotistas(request):
    """
    Vista de administración: muestra todos los tarotistas registrados.
    """
    tarotistas = Tarotista.objects.select_related("usuario").order_by(
        "usuario__first_name", "usuario__last_name", "usuario__username"
    )
    return render(
        request,
        "lista_tarotistas.html",
        {
            "tarotistas": tarotistas,
        },
    )


# -------------------------------------------------------------------
# PERFIL TAROTISTA (detalle)
# -------------------------------------------------------------------
@login_required
def perfil_tarotista(request, tarotista_id):
    """
    Perfil público/administrativo de un tarotista.

    - El tarotista puede ver su propio perfil.
    - Un admin/staff puede ver el perfil de cualquier tarotista.
    """
    tarotista = get_object_or_404(
        Tarotista.objects.select_related("usuario"), id=tarotista_id
    )

    # Permitir ver:
    #  - el propio tarotista
    #  - o staff/superuser
    if request.user != tarotista.usuario and not _es_admin(request.user):
        raise Http404("No tienes permiso para ver este tarotista.")

    citas = (
        Cita.objects.filter(tarotista=tarotista)
        .select_related("usuario")
        .order_by("-fecha", "-hora_inicio")
    )

    return render(
        request,
        "perfil_tarotista.html",
        {
            "tarotista": tarotista,
            "usuario_perfil": tarotista.usuario,
            "citas": citas,
        },
    )


# -------------------------------------------------------------------
# EDITAR TAROTISTA (para administración)
# -------------------------------------------------------------------
@login_required
@user_passes_test(_es_admin)
def editar_tarotista(request, tarotista_id):
    """
    Edición de información del tarotista (solo admin/staff).
    """
    tarotista = get_object_or_404(Tarotista, id=tarotista_id)

    if request.method == "POST":
        form = TarotistaForm(request.POST, request.FILES, instance=tarotista)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarotista actualizado correctamente.")
            return redirect("tarotistas:perfil_tarotista", tarotista_id=tarotista.id)
    else:
        form = TarotistaForm(instance=tarotista)

    return render(
        request,
        "editar_tarotista.html",
        {
            "form": form,
            "tarotista": tarotista,
        },
    )


# -------------------------------------------------------------------
# LISTA DE CLIENTES DEL TAROTISTA
# -------------------------------------------------------------------
@login_required
def lista_clientes(request):
    """
    Lista de clientes con los que el tarotista ha tenido citas.
    Solo accesible para usuarios marcados como tarotistas.
    """
    if not _es_tarotista(request.user):
        raise Http404("Solo los tarotistas pueden ver sus clientes.")

    tarotista = request.user.tarotista

    citas = (
        Cita.objects.filter(tarotista=tarotista)
        .select_related("usuario")
        .order_by("-fecha", "-hora_inicio")
    )

    clientes_dict = {}
    for cita in citas:
        if cita.usuario_id and cita.usuario not in clientes_dict:
            clientes_dict[cita.usuario_id] = cita.usuario

    clientes = list(clientes_dict.values())

    return render(
        request,
        "lista_clientes.html",
        {
            "clientes": clientes,
            "tarotista": tarotista,
        },
    )


# -------------------------------------------------------------------
# CALENDARIO / DISPONIBILIDAD DEL TAROTISTA
# -------------------------------------------------------------------
@login_required
def calendario(request):
    """
    Punto de entrada histórico para el calendario del tarotista.

    Para simplificar, si ya tienes una vista en core (por ejemplo core:calendario),
    podemos redirigir allí. Si más adelante quieres un calendario propio aquí,
    se puede implementar.
    """
    # Si tienes una vista específica en core para el calendario, redirige:
    try:
        from django.urls import reverse
        from django.shortcuts import redirect

        return redirect("core:calendario")
    except Exception:
        # Si no existe esa URL, al menos mostramos una plantilla simple
        if not _es_tarotista(request.user) and not _es_admin(request.user):
            raise Http404("No tienes permiso para ver el calendario.")

        return render(request, "calendario.html", {})


# -------------------------------------------------------------------
# BLOQUEAR / DESBLOQUEAR USUARIO
# -------------------------------------------------------------------
@login_required
@user_passes_test(_es_admin)
def bloquear_usuario(request, usuario_id):
    """
    Alterna el estado 'bloqueado' de un usuario.
    Usado desde las pantallas de administración / lista de clientes.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuario.bloqueado = not usuario.bloqueado
    usuario.save(update_fields=["bloqueado"])

    if usuario.bloqueado:
        messages.success(request, f"El usuario {usuario.username} fue bloqueado.")
    else:
        messages.success(request, f"El usuario {usuario.username} fue desbloqueado.")

    return redirect("tarotistas:lista_tarotistas")

