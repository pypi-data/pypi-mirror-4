from django.conf import settings
from django.utils.importlib import import_module

DISPOSE_MEDIA = getattr(settings, 'DISPOSE_MEDIA',{})
