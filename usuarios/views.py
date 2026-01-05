def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    if usuario is not None and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        messages.success(request, '¡Cuenta activada! Ya puedes iniciar sesión.')
        return redirect('usuarios:login')
    else:
        messages.error(request, 'El enlace de activación no es válido o expiró.')
        return redirect('usuarios:login')
from .password_reset_utils import (
    generar_codigo_verificacion,
    guardar_codigo_en_cache,
    obtener_codigo_de_cache,
    eliminar_codigo_de_cache,
    enviar_codigo_reset
)
from django.contrib.auth.hashers import make_password
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'password_reset_request.html', {'error': 'Debes ingresar tu correo.'})
        try:
            usuario = Usuario.objects.get(email__iexact=email)
        except Usuario.DoesNotExist:
            return render(request, 'password_reset_request.html', {'error': 'No existe una cuenta con ese correo.'})
        code = generar_codigo_verificacion()
        guardar_codigo_en_cache(email, code)
        enviar_codigo_reset(email, code)
        request.session['reset_email'] = email
        return redirect('usuarios:password_reset_verify')
    return render(request, 'password_reset_request.html')

def password_reset_verify(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('usuarios:password_reset_request')
    if request.method == 'POST':
        code = request.POST.get('code')
        code_cache = obtener_codigo_de_cache(email)
        if code and code_cache and code == code_cache:
            request.session['reset_verified'] = True
            return redirect('usuarios:password_reset_form')
        else:
            return render(request, 'password_reset_verify.html', {'error': 'Código incorrecto o expirado.'})
    return render(request, 'password_reset_verify.html')

def password_reset_form(request):
    email = request.session.get('reset_email')
    verified = request.session.get('reset_verified')
    if not (email and verified):
        return redirect('usuarios:password_reset_request')
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not password1 or not password2:
            return render(request, 'password_reset_form.html', {'error': 'Debes ingresar ambas contraseñas.'})
        if password1 != password2:
            return render(request, 'password_reset_form.html', {'error': 'Las contraseñas no coinciden.'})
        try:
            usuario = Usuario.objects.get(email__iexact=email)
            usuario.password = make_password(password1)
            usuario.save()
            eliminar_codigo_de_cache(email)
            request.session.pop('reset_email', None)
            request.session.pop('reset_verified', None)
            messages.success(request, 'Contraseña restablecida correctamente. Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
        except Usuario.DoesNotExist:
            return render(request, 'password_reset_form.html', {'error': 'No existe una cuenta con ese correo.'})
    return render(request, 'password_reset_form.html')
# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Value, CharField
from django.db.models.functions import Replace, Lower
from .models import Usuario
from .utils import validar_rut_detalle, validar_rut, normalize_rut
from .email_utils import enviar_email_verificacion
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator


def registro(request):
    """
    Vista para el registro de nuevos usuarios.
    Crea la cuenta y realiza inicio de sesión automático.
    """
    if request.method == 'POST':
        # Collect form data and prepare error map for the template
        errores = {}
        data = request.POST.dict()

        username = request.POST.get('username')
        email = request.POST.get('email')
        if request.method == 'POST':
            errores = {}
            data = request.POST.dict()

            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            rut = request.POST.get('rut', '').strip()

            # Validaciones básicas
            if not all([username, email, password1, password2]):
                messages.error(request, 'Todos los campos obligatorios deben completarse.')
                return render(request, 'registro.html', {'data': data, 'errores': errores})

            if password1 != password2:
                errores['password'] = 'Las contraseñas no coinciden.'
                return render(request, 'registro.html', {'data': data, 'errores': errores})

            # Validar formato de RUT si fue provisto
            if rut:
                valido, motivo = validar_rut_detalle(rut)
                if not valido:
                    if motivo == 'format':
                        errores['rut'] = 'Formato de RUT inválido. Verifica el formato (ej: 12.345.678-5).'
                    elif motivo == 'dv':
                        errores['rut'] = (
                            'El RUT tiene formato correcto pero no corresponde a un RUT válido. Revisa el número o verifica tus datos.'
                        )
                    else:
                        errores['rut'] = 'RUT inválido.'
                    return render(request, 'registro.html', {'data': data, 'errores': errores})

                normalized = normalize_rut(rut)
                rut_qs = Usuario.objects.annotate(
                    rut_norm=Lower(
                        Replace(
                            Replace(
                                'rut',
                                Value('.', output_field=CharField()),
                                Value('', output_field=CharField()),
                                output_field=CharField()
                            ),
                            Value('-', output_field=CharField()),
                            Value('', output_field=CharField()),
                            output_field=CharField()
                        ),
                        output_field=CharField()
                    )
                ).filter(rut_norm=normalized.lower())
                if rut_qs.exists():
                    errores['rut'] = (
                        'El RUT ingresado ya está registrado. Si es tu cuenta, inicia sesión o recupera tu contraseña.'
                    )
                    return render(request, 'registro.html', {'data': data, 'errores': errores})

            username_clean = (username or '').strip()
            email_clean = (email or '').strip().lower()

            if Usuario.objects.filter(username__iexact=username_clean).exists():
                errores['username'] = 'El nombre de usuario ya está en uso. Elige otro.'
                return render(request, 'registro.html', {'data': data, 'errores': errores})

            if email_clean and Usuario.objects.filter(email__iexact=email_clean).exists():
                errores['email'] = 'El correo ya está registrado. Inicia sesión o usa otro correo.'
                return render(request, 'registro.html', {'data': data, 'errores': errores})

            # Intentar crear usuario y manejar errores de unicidad con un mensaje amigable
            try:
                usuario = Usuario.objects.create_user(
                    username=username_clean,
                    email=email_clean,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                    rut=normalize_rut(rut) if rut else '',
                    is_active=False
                )
                enviar_email_verificacion(usuario, request)
                messages.success(request, 'Te enviamos un correo para verificar tu cuenta. Revisa tu bandeja de entrada.')
                return redirect('usuarios:login')
            except IntegrityError:
                errores['rut'] = (
                    'No fue posible crear la cuenta porque el RUT ya está registrado. ' 
                    'Si este es tu RUT, inicia sesión o usa la recuperación de contraseña.'
                )
                return render(request, 'registro.html', {'data': data, 'errores': errores})
            except Exception as e:
                messages.error(request, 'Error al crear la cuenta. Por favor inténtalo de nuevo más tarde.')
                return render(request, 'registro.html', {'data': data, 'errores': errores})

        return render(request, 'registro.html')

    return render(request, 'registro.html')


def login_view(request):
    """
    Maneja el inicio de sesión de usuarios.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.bloqueado:
                messages.error(request, 'Tu cuenta ha sido bloqueada.')
                return redirect('usuarios:login')

            login(request, user)
            return redirect('core:home')  # Redirige al home principal
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


def logout_view(request):
    """
    Cierra la sesión del usuario.
    """
    logout(request)
    return redirect('usuarios:login')


@login_required
def perfil(request):
    """
    Muestra la página de perfil del usuario autenticado.
    """
    return render(request, 'perfil.html')


@login_required
def editar_perfil(request):
    """
    Permite al usuario editar su información personal.
    """
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', getattr(user, 'bio', ''))
        user.telefono = request.POST.get('telefono', getattr(user, 'telefono', ''))
        user.apodo = request.POST.get('apodo', getattr(user, 'apodo', ''))

        # Manejo de avatar
        if 'imagen' in request.FILES:
            user.avatar = request.FILES['imagen']

        user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('usuarios:perfil')

    return render(request, 'gestionperfil.html')
