from django import template
from django_helpers import get_settings_val
from django_helpers.helpers.templatetags import TemplateNode, parse_args
from django_helpers.apps.nivo_slider.models import NivoSlider as NivoSliderModel
from django_helpers.apps.nivo_slider import NivoSlider, use_theme
from django_helpers.templatetags.static_manger import add_js_file, add_css_file

__author__ = 'ajumell'

add_js_file('nivo-slider/js/jquery.nivo.slider.pack.js')
add_css_file('nivo-slider/css/nivo-slider.css')

for x in get_settings_val('NIVO_SLIDER_THEMES', []):
    use_theme(x)


class NivoSliderNode(TemplateNode):
    def render(self, context):
        name = self.args[0].resolve(context)
        slider_obj = NivoSliderModel.objects.get(name=name)
        slider = NivoSlider()
        for attr in dir(slider_obj):
            if not attr.startswith('__'):
                if hasattr(slider, attr):
                    val = getattr(slider_obj, attr)
                    setattr(slider, attr, val)
        slider.slider_id = slider_obj.id
        for img in slider_obj.slides():
            url = img.image.url
            caption = img.caption
            alt_text = img.alternate_text
            link = img.link
            transition = img.transition
            slider.add_image(url, caption, alt_text, link, transition)
        return str(slider)

register = template.Library()

@register.tag
def nivo_slider(parser, token):
    bits = token.split_contents()
    args, kwargs = parse_args(bits, parser)
    return NivoSliderNode(args, kwargs)