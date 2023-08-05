from .settings import AUTOLOAD_MODULES

# init ;-)
import django_internal_urls.defaultmodules
if AUTOLOAD_MODULES:
    import django_internal_urls.autoload

