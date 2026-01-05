# core/context_processors.py

def user_roles(request):
    """
    Variables globales para templates.
    - is_tarotista: True si el usuario tiene flag es_tarotista o si existe el OneToOne 'tarotista'
    """
    user = getattr(request, "user", None)

    is_tarotista = False
    if user and getattr(user, "is_authenticated", False):
        is_tarotista = bool(getattr(user, "es_tarotista", False) or hasattr(user, "tarotista"))

    return {
        "is_tarotista": is_tarotista
    }
