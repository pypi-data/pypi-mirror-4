from . import register

def django_url(args, kwargs):
    from django.core.urlresolvers import reverse, NoReverseMatch
    if len(args) < 1:
        return ''
    url = args[0]
    args = args[1:]
    try:
        return reverse(url, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return ''

register('url', django_url)

