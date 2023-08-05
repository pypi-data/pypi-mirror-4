from django_helpers.helpers.templatetags import TemplateNode, parse_args
from django_helpers.helpers.views import render_to_string
from django_helpers.templatetags.static_manger import register, add_jquery


__author__ = 'ajumell'

class BackToTopNode(TemplateNode):

    def __init__(self, args, kwargs):
        TemplateNode.__init__(self, args, kwargs)
        add_jquery()

    def render(self, context):
        args = self.args
        kwargs = self.kwarg
        if len(args) > 0:
            template = args[0].resolve(context)
        else:
            template = 'tags/extras/back-to-top.html'

        if kwargs.has_key('position'):
            p = kwargs['position']
            p = p.resolve(context)
        else:
            p = 100

        return render_to_string(template,{
            'position': p
        })

@register.tag
def back_to_top(parser, token):
    bits = token.split_contents()
    args, kwargs = parse_args(bits, parser)
    return BackToTopNode(args, kwargs)
