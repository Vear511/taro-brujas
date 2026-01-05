from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Value, CharField
from django.db.models.functions import Replace, Lower

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Usuario
from .utils import validar_rut_detalle, normalize_rut
from .email_utils import enviar_email_verificacion

from .password_reset_utils import (
    generar_codigo_verificacion,
    guardar_codigo_en_cache,
    obtener_codigo_de_cache,
    eliminar_codigo_de_cache,
    enviar_codigo_reset,
)


# --------------------------------------------------
# Activación de cuenta
# --------------------------------------------------

def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.email_verificado = True
        usuario.save(update_fields=["is_active", "email_verificado"])
        messages.success(request, "¡Cuenta activada! Ya puedes iniciar sesión.")
        return redirect("usuarios:login")

    messages.error(request, "El enlace de activación no es válido o expiró.")
    return redirect("usuarios:login")


# --------------------------------------------------
# Registro
# --------------------------------------------------

def registro(request):
    if request.method == "POST":
        errores = {}
        data = request.POST.dict()

        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        rut_raw = (request.POST.get("rut") or "").strip()

        if not all([username, email, password1, password2]):
            messages.error(request, "Todos los campos obligatorios deben completarse.")
            return render(request, "registro.html", {"data": data, "errores": errores})

        if password1 != password2:
            errores["password"] = "Las contraseñas no coinciden."
            return render(request, "registro.html", {"data": data, "errores": errores})

        # ✔ Validar contraseña usando los mismos validadores que en todo el sistema
        try:
            # Puedes pasar un usuario temporal si quieres validar similaridad de atributos
            tmp_user = Usuario(username=username, email=email, first_name=first_name, last_name=last_name)
            validate_password(password1, user=tmp_user)
        except ValidationError as e:
            errores["password"] = " ".join(e.messages)
            return render(request, "registro.html", {"data": data, "errores": errores})

        # Validación RUT si fue provisto
        rut_norm = None
        if rut_raw:
            valido, motivo = validar_rut_detalle(rut_raw)
            if not valido:
                if motivo == "format":
                    errores["rut"] = "Formato de RUT inválido. Use 12.345.678-5"
                elif motivo == "dv":
                    errores["rut"] = "RUT no válido: dígito verificador incorrecto."
                else:
                    errores["rut"] = "RUT inválido."
                return render(request, "registro.html", {"data": data, "errores": errores})

            rut_norm = normalize_rut(rut_raw)

            # Check duplicado ignorando puntos/guión
            rut_qs = Usuario.objects.annotate(
                rut_norm_db=Lower(
                    Replace(
                        Replace(
                            "rut",
                            Value(".", output_field=CharField()),
                            Value("", output_field=CharField()),
                            output_field=CharField(),
                        ),
                        Value("-", output_field=CharField()),
                        Value("", output_field=CharField()),
                        output_field=CharField(),
                    )
                )
            ).filter(rut_norm_db=(rut_norm or "").lower())

            if rut_qs.exists():
                errores["rut"] = "El RUT ingresado ya está registrado."
                return render(request, "registro.html", {"data": data, "errores": errores})

        if Usuario.objects.filter(username__iexact=username).exists():
            errores["username"] = "El nombre de usuario ya está en uso."
            return render(request, "registro.html", {"data": data, "errores": errores})

        if Usuario.objects.filter(email__iexact=email).exists():
            errores["email"] = "El correo ya está registrado."
            return render(request, "registro.html", {"data": data, "errores": errores})

        try:
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                rut=rut_norm,          # None si no viene
                is_active=False,       # requiere activación
                email_verificado=False,
            )
            enviar_email_verificacion(usuario, request)
            messages.success(request, "Te enviamos un correo para verificar tu cuenta.")
            return redirect("usuarios:login")

        except IntegrityError:
            errores["general"] = "No fue posible crear la cuenta (usuario/email/RUT duplicado)."
            return render(request, "registro.html", {"data": data, "errores": errores})
        except Exception:
            mensajes = "Error al crear la cuenta. Intenta nuevamente."
            messages.error(request, mensajes)
            return render(request, "registro.html", {"data": data, "errores": errores})

    return render(request, "registro.html")


# --------------------------------------------------
# Login / Logout
# --------------------------------------------------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if getattr(user, "bloqueado", False):
                messages.error(request, "Tu cuenta ha sido bloqueada.")
                return redirect("usuarios:login")

            login(request, user)
            return redirect("core:home")

        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("usuarios:login")


# --------------------------------------------------
# Perfil
# --------------------------------------------------

@login_required
def perfil(request):
    return render(request, "perfil.html")


@login_required
def editar_perfil(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)

        # Campos extra
        user.apodo = request.POST.get("apodo", getattr(user, "apodo", ""))
        user.telefono = request.POST.get("telefono", getattr(user, "telefono", ""))
        user.bio = request.POST.get("bio", getattr(user, "bio", ""))

        # ✅ HTML usa name="avatar"
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]

        user.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("usuarios:perfil")

    return render(request, "gestionperfil.html")


# --------------------------------------------------
# Password reset con código
# --------------------------------------------------

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return render(
                request,
                "password_reset_request.html",
                {"error": "Debes ingresar tu correo."},
            )

        try:
            usuario = Usuario.objects.get(email__iexact=email)
        except Usuario.DoesNotExist:
            return render(
                request,
                "password_reset_request.html",
                {"error": "No existe una cuenta con ese correo."},
            )

        code = generar_codigo_verificacion()
        guardar_codigo_en_cache(email, code)
        enviar_codigo_reset(email, code)
        request.session["reset_email"] = email
        return redirect("usuarios:password_reset_verify")

    return render(request, "password_reset_request.html")


def password_reset_verify(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("usuarios:password_reset_request")

    if request.method == "POST":
        code = request.POST.get("code")
        code_cache = obtener_codigo_de_cache(email)
        if code and code_cache and code == code_cache:
            request.session["reset_verified"] = True
            return redirect("usuarios:password_reset_form")
        return render(
            request,
            "password_reset_verify.html",
            {"error": "Código incorrecto o expirado."},
        )

    return render(request, "password_reset_verify.html")


def password_reset_form(request):
    email = request.session.get("reset_email")
    verified = request.session.get("reset_verified")
    if not (email and verified):
        return redirect("usuarios:password_reset_request")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or not password2:
            return render(
                request,
                "password_reset_form.html",
                {"error": "Debes ingresar ambas contraseñas."},
            )

        if password1 != password2:
            return render(
                request,
                "password_reset_form.html",
                {"error": "Las contraseñas no coinciden."},
            )

        try:
            usuario = Usuario.objects.get(email__iexact=email)

            # ✔ Validar contraseña con los mismos validadores del sistema
            try:
                validate_password(password1, user=usuario)
            except ValidationError as e:
                # Mostramos todos los mensajes juntos
                return render(
                    request,
                    "password_reset_form.html",
                    {"error": " ".join(e.messages)},
                )

            # Si todo OK, guardamos la nueva contraseña
            usuario.password = make_password(password1)
            usuario.save()

            # Limpiar cache y sesión
            eliminar_codigo_de_cache(email)
            request.session.pop("reset_email", None)
            request.session.pop("reset_verified", None)

            messages.success(
                request,
                "Contraseña restablecida correctamente. Ya puedes iniciar sesión.",
            )
            return redirect("usuarios:login")

        except Usuario.DoesNotExist:
            return render(
                request,
                "password_reset_form.html",
                {"error": "No existe una cuenta con ese correo."},
            )

    return render(request, "password_reset_form.html")
