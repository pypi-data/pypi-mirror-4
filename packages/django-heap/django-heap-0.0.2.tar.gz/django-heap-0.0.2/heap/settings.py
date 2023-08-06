from django.conf import settings

HEAP_APP_ID = getattr(settings, 'HEAP_APP_ID')
HEAP_TRACK_SUPERUSER = getattr(settings, 'HEAP_TRACK_SUPERUSER', True)
HEAP_AUTO_ID_USER = getattr(settings, 'HEAP_AUTO_ID_USER', False)
