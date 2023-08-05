import re
from django_helpers.helpers.templatetags import parse_args
from django_helpers.helpers.views import render_to_string

__author__ = 'ajumell'

from django import template
from django.template.base import TemplateSyntaxError
from django.template.defaulttags import Node

youtube_regexp = re.compile(r"^(http://)?(www\.)?(youtube\.com/watch)?(.*)(\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})")
register = template.Library()

class YoutubeNode(Node):

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

        self.video_id = args[0]
        self.width = kwargs.get('width', '800px')
        self.height = kwargs.get('height', "400px")
        self.full_screen = kwargs.get('fullscreen', True)

    def render(self, context):
        url = self.video_id.resolve(context)
        width = self.width.resolve(context)
        height = self.height.resolve(context)

        try:
            full_screen = self.full_screen.resolve(context)
        except Exception:
            full_screen = self.full_screen

        if full_screen:
            full_screen = "allowfullscreen"
        else:
            full_screen = ""

        match = youtube_regexp.match(url)
        if not match:
            return ""
        video_id = match.group('id')
        return render_to_string('tags/video/youtube.html',{
            'video_id': video_id,
            'width': width,
            'height': height,
            'full_screen': full_screen
        })

@register.tag
def youtube(parser, token):
    bits = token.split_contents()
    args, kwargs = parse_args(bits, parser)
    if len(args) < 1:
        raise TemplateSyntaxError("'%s' takes at least one arguments." % bits[0])
    return YoutubeNode(args, kwargs)


