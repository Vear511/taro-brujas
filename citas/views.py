from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CitaForm
from .models import Cita


@login_required
def agendar_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.cliente = request.user
            cita.estado = "pendiente"
            cita.save()

            # Enviar correo de confirmación
            from django.core.mail import send_mail
            from django.conf import settings
            from django.utils import timezone

            # Nombre tarotista (modelo Tarotista tiene relación .usuario)
            tarotista_nombre = (
                cita.tarotista.usuario.get_full_name()
                if hasattr(cita.tarotista, "usuario")
                else str(cita.tarotista)
            )

            fecha_hora = cita.fecha_hora
            if timezone.is_naive(fecha_hora):
                fecha_hora = timezone.make_aware(
                    fecha_hora, timezone.get_current_timezone()
                )

            fecha = fecha_hora.strftime("%d/%m/%Y %H:%M")

            servicio = getattr(cita, "servicio", "Consulta")

            subject = "Confirmación de reserva de cita"
            message = (
                f"Hola {request.user.get_full_name() or request.user.username},\n\n"
                f"Tu cita ha sido reservada con éxito.\n\n"
                f"Tarotista: {tarotista_nombre}\n"
                f"Fecha y hora: {fecha}\n"
                f"Tipo de servicio: {servicio}\n\n"
                "Gracias por confiar en Brujitas."
            )

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

            messages.success(
                request,
                "Tu cita fue agendada correctamente. "
                "Se ha enviado un correo de confirmación.",
            )
            return redirect("citas:mis_citas")
    else:
        form = CitaForm()

    return render(request, "agendar_cita.html", {"form": form})


@login_required
def mis_citas(request):
    """
    Muestra las citas del usuario.
    - Si es tarotista: citas donde ella es la tarotista.
    - Si es clienta: citas donde ella es la cliente.
    Todas ordenadas desde la más próxima (fecha_hora ascendente).
    """
    user = request.user

    if getattr(user, "es_tarotista", False):
        # Citas donde la tarotista asociada a este usuario atiende
        citas = (
            Cita.objects
            .filter(tarotista__usuario=user)
            .order_by("fecha_hora")
        )
    else:
        # Citas donde el usuario es cliente
        citas = (
            Cita.objects
            .filter(cliente=user)
            .order_by("fecha_hora")
        )

    return render(request, "mis_citas.html", {"citas": citas})


@login_required
def detalle_cita(request, cita_id):
    """
    Muestra el detalle de una cita específica del usuario (como cliente).
    """
    cita = get_object_or_404(Cita, id=cita_id, cliente=request.user)
    return render(request, "detalle_cita.html", {"cita": cita})


@login_required
def editar_cita(request, cita_id):
    """
    Permite al usuario editar una cita que él haya agendado.
    """
    cita = get_object_or_404(Cita, id=cita_id, cliente=request.user)

    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu cita ha sido actualizada correctamente.")
            return redirect("citas:mis_citas")
    else:
        form = CitaForm(instance=cita)

    return render(request, "editar_cita.html", {"form": form, "cita": cita})


@login_required
def eliminar_cita(request, cita_id):
    """
    Permite al usuario eliminar una cita que él haya agendado.
    """
    cita = get_object_or_404(Cita, id=cita_id, cliente=request.user)

    if request.method == "POST":
        cita.delete()
        messages.success(request, "Tu cita ha sido eliminada correctamente.")
        return redirect("citas:mis_citas")

    return render(request, "eliminar_cita.html", {"cita": cita})
