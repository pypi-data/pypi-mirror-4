from . import settings

def heap(request):
    is_super = request.user.is_authenticated() and request.user.is_superuser
    return dict(
        HEAP_APP_ID=settings.HEAP_APP_ID,
        HEAP_USER_UNTRACKABLE=(not settings.HEAP_TRACK_SUPERUSER) and is_super,
        HEAP_AUTO_ID_USER=settings.HEAP_AUTO_ID_USER
    )
