from django_helpers.helpers.views import render_to_string
from django_helpers.templatetags.static_manger import add_js_file, add_jquery

__author__ = 'ajumell'

class FormRenderer(object):
    form_submit = 'Submit'
    focus_first = None
    form_id = None
    has_validation = True
    has_rules = True
    template = 'form-renderer/form.html'
    method = 'POST'
    form_action = ''

    def __init__(self, form, request=None, form_id=None, csrf_token=None, template=None):

        add_jquery()
        add_js_file('form-renderer/js/jquery.validate.min.js')

        self.form = form
        self.request = request
        self.csrf_token = csrf_token

        if template is not None:
            self.template = template

        if self.request is None and csrf_token is None:
            raise Exception("Either request or csrf_token is needed.")

        if form_id is not None:
            self.form_id = form_id


    def __str__(self):
        return self.render()


    def __unicode__(self):
        return self.render()

    def render(self):
        if self.form_id is None:
            raise Exception("Form ID is necessary")

        return render_to_string(self.template, {
            'form': self.form,
            'form_submit': self.form_submit,
            'focus_first': self.focus_first,
            'form_id': self.form_id,
            'has_validation': self.has_validation,
            'has_rules': self.has_rules,
            'method': self.method,
            'form_action': self.form_action,
            'csrf_token_html': self.csrf_token
        }, self.request)
