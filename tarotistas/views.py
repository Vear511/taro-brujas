# tarotistas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.models import Usuario
from .models import Tarotista


# ======================================================
# AGREGAR TAROTISTA (SOLO STAFF)
# ======================================================
@user_passes_test(lambda u: u.is_staff)
def agregar_tarotista(request):
    if request.method == 'POST':
        try:
            # Crear usuario asociado al tarotista
            usuario = Usuario.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name']
            )

            # Crear tarotista
            tarotista = Tarotista.objects.create(
                usuario=usuario,
                especialidad=request.POST['especialidad'],
                experiencia=int(request.POST['experiencia']),
                precio_por_sesion=float(request.POST['precio_por_sesion']),
                descripcion=request.POST['descripcion'],
                # ✅ CORRECCIÓN REAL
                disponible='disponible' in request.POST
            )

            return redirect('gestion_tarotistas')

        except Exception as e:
            return render(request, 'agregar_tarotista.html', {
                'error': f'Error al crear tarotista: {str(e)}'
            })

    return render(request, 'agregar_tarotista.html')


# ======================================================
# LISTA DE TAROTISTAS DISPONIBLES (CLIENTES)
# ======================================================
def lista_tarotistas(request):
    tarotistas = Tarotista.objects.filter(disponible=True)
    return render(request, 'lista_tarotistas.html', {
        'tarotistas': tarotistas
    })


# ======================================================
# PERFIL DE TAROTISTA
# ======================================================
def perfil_tarotista(request, tarotista_id):
    tarotista = get_object_or_404(Tarotista, id=tarotista_id)
    return render(request, 'perfil_tarotista.html', {
        'tarotista': tarotista
    })


# ======================================================
# LISTA DE CLIENTES (SOLO TAROTISTAS)
# ======================================================
@login_required
@user_passes_test(lambda u: hasattr(u, 'tarotista'))
def lista_clientes(request):
    clientes = Usuario.objects.exclude(
        tarotista__isnull=False
    ).exclude(
        is_staff=True
    )

    return render(request, 'lista_clientes.html', {
        'clientes': clientes
    })


# ======================================================
# BLOQUEAR / DESBLOQUEAR USUARIO
# ======================================================
@login_required
@user_passes_test(lambda u: hasattr(u, 'tarotista'))
def bloquear_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.bloqueado = not usuario.bloqueado
    usuario.save()

    return redirect('tarotistas:lista_clientes')


# ======================================================
# CALENDARIO DE LA TAROTISTA
# ======================================================
@login_required
def calendario(request):
    context = {
        'tarotista': request.user.tarotista if hasattr(request.user, 'tarotista') else None,
        # aquí puedes agregar citas, horarios, etc.
    }

    return render(request, 'calendario.html', context)
