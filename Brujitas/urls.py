from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Core (página principal)
    path('', include('core.urls', namespace='core')),

    # Gestión de usuarios
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),

    # Tarotistas
    path('tarotistas/', include('tarotistas.urls', namespace='tarotistas')),

    # Citas
    path('citas/', include('citas.urls', namespace='citas')),

    # Auth (opcional)
    path('accounts/', include('django.contrib.auth.urls')),
    # Usuarios app routes (already defined above)

]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
