from django.conf import settings

HEAP_APP_ID = getattr(settings, 'HEAP_APP_ID')
HEAP_TRACK_SUPERUSER = getattr(settings, 'HEAP_TRACK_SUPERUSER', True)
