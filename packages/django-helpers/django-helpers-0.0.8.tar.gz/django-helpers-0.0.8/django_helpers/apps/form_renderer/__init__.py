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
    field_template = 'form-renderer/form-display.html'
    method = 'POST'
    form_action = ''
    field_sets = None
    render_extras = False
    ignore_extras = True

    def __init__(self, form, request=None, form_id=None, csrf_token=None, template=None):
        add_jquery()
        add_js_file('form-renderer/js/jquery.validate.min.js')

        self.form = form
        self.request = request
        self.csrf_token = csrf_token

        if self.field_sets is not None:
            self.field_sets = self.field_sets[:]

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

        form = self.form
        mew_field_sets = []
        used_fields = []

        if hasattr(self, 'field_sets') and self.field_sets is not None:
            for field_set in self.field_sets:
                new_field_set = {}
                new_fields = []

                for field_name in field_set['fields']:
                    field = form[field_name]
                    used_fields.append(field_name)
                    new_fields.append(field)

                new_field_set['title'] = field_set['title']
                new_field_set['fields'] = new_fields
                mew_field_sets.append(new_field_set)

        if not self.ignore_extras:
            fields_not_in_field_sets = []
            for field in form:
                if field.name not in used_fields:
                    fields_not_in_field_sets.append(field)
            if self.render_extras:
                if len(fields_not_in_field_sets):
                    mew_field_sets.append({
                        'title': 'Others',
                        'fields': fields_not_in_field_sets
                    })
            else:
                raise Exception("All fields in the form is not present in the form sets")

        return render_to_string(self.template, {
            'form': self.form,
            'form_submit': self.form_submit,
            'focus_first': self.focus_first,
            'form_id': self.form_id,
            'field_sets': mew_field_sets,
            'has_validation': self.has_validation,
            'has_rules': self.has_rules,
            'method': self.method,
            'form_action': self.form_action,
            'csrf_token_html': self.csrf_token,
            'field_template': self.field_template
        }, self.request)
