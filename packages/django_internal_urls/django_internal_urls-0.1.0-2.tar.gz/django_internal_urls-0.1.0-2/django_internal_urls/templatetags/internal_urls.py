from django.template.defaulttags import kwarg_re
from django import template
from django.conf import settings

register = template.Library()


def parse_args(parser, bits):
    # see django.templatetags.future: url, line 80
    args = []
    kwargs = {}
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise template.TemplateSyntaxError("Malformed arguments to iurl tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
    
    return args, kwargs, asvar


class InternalUrlNode(template.Node):
    def __init__(self, module_name, args, kwargs, asvar):
        self.module_name = module_name
        self.args, self.kwargs, self.asvar = args, kwargs, asvar
    
    def render(self, context):
        from .. import modules
        module_name = self.module_name.resolve(context)
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.iteritems()])
        try:
            module = modules.get(module_name)
        except modules.ModuleDoesNotExist:
            raise RuntimeError("valid module required")
        url = module(args, kwargs)
        if self.asvar:
            context[self.asvar] = url
            return ''
        return url


@register.tag
def iurl(parser, token):
    """Display a form and handles form-saving
    
    {% iurl "module" arg1 arg2 kwarg1=foo kwarg2=bar %}
    """
    parts = token.split_contents()
    if len(parts) < 2:
        raise template.TemplateSyntaxError("%r tag requires as least one argument" % parts[0])
    module_name = parser.compile_filter(parts[1])
    args, kwargs, asvar = parse_args(parser, parts[2:])
    return InternalUrlNode(module_name, args, kwargs, asvar)

