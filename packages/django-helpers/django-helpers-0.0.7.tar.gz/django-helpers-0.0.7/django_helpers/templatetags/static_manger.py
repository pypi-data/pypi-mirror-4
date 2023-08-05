__author__ = 'ajumell'

from django_helpers.helpers.templatetags import TemplateNode
from django.contrib.staticfiles import finders
from django import template

JS_FILES = []
CSS_FILES = []

def add_js_file(name):
    if JS_FILES.count(name) == 0:
        JS_FILES.append(name)


def add_css_file(name):
    if CSS_FILES.count(name) == 0:
        CSS_FILES.append(name)

# TODO: Validate if files exits
# TODO: Find a method to make this to one file
# TODO: Check absolute urls in included files

def get_code(template, array):
    from django.conf import settings

    static_url = getattr(settings, 'STATIC_URL')
    code = ""
    for f in array:
        if f.startswith("http://") or f.startswith("https://"):
            s = ""
        else:
            s = static_url
            absolute_path = finders.find(f)
            if not absolute_path:
                raise Exception("Static file cannot be found.")
        code += template % (s, f)
    return code


def get_js_code():
    return get_code('<script type="text/javascript" src="%s%s"></script>', JS_FILES)

def get_css_code():
    return get_code('<link rel="stylesheet" href="%s%s" />', CSS_FILES)

register = template.Library()

class StaticFilesNode(TemplateNode):
    def render(self, context):
        return get_css_code() + get_js_code()


@register.tag
def static_files(parser, token):
    return StaticFilesNode()


def add_jquery():
    add_js_file('js/jquery-1.7.1.min.js')


def add_jquery_ui():
    add_js_file('js/jquery-ui.js')
