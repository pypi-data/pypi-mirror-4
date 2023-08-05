from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

for app in settings.INSTALLED_APPS:
    if '.' not in app:
        continue
    mod = import_module(app)
    try:
        import_module('%s.internal_urls' % app)
    except:
        if module_has_submodule(mod, 'internal_urls'):
            raise

