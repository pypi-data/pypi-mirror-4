from django.conf import settings

AUTOLOAD_MODULES = getattr(settings, 'INTERNAL_URLS_AUTOLOAD_MODULES', False)

