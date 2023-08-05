def resolve(module, args=None, kwargs=None):
    from . import modules
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    try:
        handler = modules.get(module)
    except module.ModuleDoesNotExist:
        return ''
    return handler(args, kwargs)
