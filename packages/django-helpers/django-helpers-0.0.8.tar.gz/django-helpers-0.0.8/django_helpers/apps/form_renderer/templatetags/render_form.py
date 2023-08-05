from django.template import TemplateSyntaxError, Node
from django.template.defaulttags import register, CsrfTokenNode
from django_helpers.apps.form_renderer import FormRenderer
from django_helpers.helpers.templatetags import parse_args

__author__ = 'ajumell'

class FormRendererNode(Node):
    def __init__(self, form, form_id, template, kwargs=None):
        self.form = form
        self.form_id = form_id
        self.template = template
        self.kwargs = kwargs

    def render(self, context):
        csrf_token = CsrfTokenNode().render(context)
        template = self.template
        form_id = self.form_id.resolve(context)
        form = self.form.resolve(context)

        obj = FormRenderer(form, form_id=form_id, csrf_token=csrf_token, template=template)
        for arg, value in self.kwargs.items():
            value = value.resolve(context)
            if hasattr(obj, arg):
                setattr(obj, arg, value)
        return obj.render()


@register.tag
def render_form(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' needs at least two arguments." % bits[0])
    args, kwargs = parse_args(bits, parser)
    template = None

    form = args[0]
    form_id = args[1]
    if len(args) > 2:
        template = bits[3]

    return FormRendererNode(form, form_id, template, kwargs)