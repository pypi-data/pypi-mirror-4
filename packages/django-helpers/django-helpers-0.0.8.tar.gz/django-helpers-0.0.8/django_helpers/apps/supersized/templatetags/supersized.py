__author__ = 'ajumell'

from django_helpers.apps.supersized import SuperSized
from django_helpers.apps.supersized.models import SuperSizedSlider
from django import template
from django_helpers.helpers.templatetags import TemplateNode, parse_args
from django_helpers.templatetags.static_manger import add_js_file, add_css_file, add_jquery, add_jquery_easing


add_jquery()
add_jquery_easing()

add_js_file('super-sized/js/supersized.3.2.7.min.js')
add_js_file('super-sized/theme/supersized.shutter.min.js')

add_css_file('super-sized/css/supersized.css')
add_css_file('super-sized/theme/supersized.shutter.css')


class SuperSizedNode(TemplateNode):
    def render(self, context):
        name = self.args[0].resolve(context)
        slider_obj = SuperSizedSlider.objects.get(name=name)
        slider = SuperSized()
        for attr in dir(slider_obj):
            if not attr.startswith('__'):
                if hasattr(slider, attr):
                    val = getattr(slider_obj, attr)
                    setattr(slider, attr, val)

        for img in slider_obj.slides():
            url = img.image.url
            try:
                thumb = img.image.thumbnail
            except Exception, dt:
                print 'Error :',dt
                thumb = url
            caption = img.caption
            link = img.link
            slider.add_slide(url, caption, thumb, link)
        return str(slider)

register = template.Library()

@register.tag
def super_sized(parser, token):
    bits = token.split_contents()
    args, kwargs = parse_args(bits, parser)
    return SuperSizedNode(args, kwargs)
