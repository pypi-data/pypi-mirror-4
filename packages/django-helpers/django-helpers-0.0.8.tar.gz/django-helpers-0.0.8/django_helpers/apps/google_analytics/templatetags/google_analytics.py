from django.template import Node, TemplateSyntaxError
from django_helpers.helpers.templatetags import parse_args
from django_helpers.helpers.views import render_to_string
from django.template.defaulttags import register

__author__ = 'ajumell'

class GoogleAnalyticsNode(Node):
    def __init__(self, code):
        self.code = code

    def render(self, context):
        code = self.code.resolve(context)
        return render_to_string('google-analytics.html',{
            'CODE': code
        })

@register.tag
def analytics_js(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' needs at least one arguments." % bits[0])
    args, kwargs = parse_args(bits, parser)
    return GoogleAnalyticsNode(*args, **kwargs)
