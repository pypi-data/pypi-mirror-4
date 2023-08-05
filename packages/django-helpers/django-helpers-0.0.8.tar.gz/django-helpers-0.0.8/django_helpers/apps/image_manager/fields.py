from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django_helpers.helpers.views import render_to_string
from models import Image
from django.db import models
from django_helpers.apps.autocomplete import AutoComplete
from django_helpers.apps.autocomplete.fields import AutoCompleteField
from django_helpers.apps.autocomplete.widgets import AutoCompleteWidget

__author__ = 'ajumell'

class ImageManagerImageAutoComplete(AutoComplete):
    name = 'image-manager'
    query_set = Image.objects.all()
    search_fields = ['name']

    def format_value(self, instance):
        return instance.name

    def get_display_url(self, instance):
        return instance.thumbnail


    def get_results(self, request, params):
        term = self.get_search_term(request)
        query = self.search(term, params)
        results = []
        for result in query:
            val = self.format_value(result)
            results.append({
                "id": result.id,
                "label": val,
                "thumbnail": self.get_display_url(result)
            })
        return results


class ImageManagerImageSelectWidget(AutoCompleteWidget):
    has_js = False
    template = 'image-manager/image-selection-field.html'

    class Media:
        # TODO: Find a method to use admin jquery
        js = ('js/jquery-1.7.1.min.js', 'js/jquery-ui.js')

    def __init__(self, attrs=None, delay=0, min_length=0, lookup=None):
        AutoCompleteWidget.__init__(self, attrs, delay, min_length, lookup)
        # Fix for admin site
        self.choices = None

    def render(self, name, value, attrs=None):
        html = AutoCompleteWidget.render(self, name, value, attrs)
        auto_complete = self.auto_complete
        instance = auto_complete.get_instance(value)
        source = reverse(self.auto_complete.name)
        value = self.value or ""
        op = render_to_string(self.template, {
            "min_length": self.min_length,
            "delay": self.delay,
            "source": source,
            "id": self.html_id,
            "name": self.name,
            "label": self.formatted_value,
            "value": value,
            "image": auto_complete.get_display_url(instance),
            "html": mark_safe(html)
        })
        return op


class ImageManagerImageSelectField(AutoCompleteField):
    widget = ImageManagerImageSelectWidget

    def __init__(self, lookup=None, required=True, widget=None, label=None, initial=None,
                 help_text=None, error_messages=None, show_hidden_initial=False,
                 validators=None, localize=False, queryset=None, to_field_name=None):
        if lookup is None:
            lookup = ImageManagerImageAutoComplete

        if queryset is not None:
            lookup.query_set = queryset

        AutoCompleteField.__init__(self, lookup, required, widget, label, initial, help_text,
            error_messages, show_hidden_initial, validators, localize)


class ImageManagerImageField(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
        models.ForeignKey.__init__(self, Image, to_field, **kwargs)

    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'queryset': self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to)
        }

        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        val = ImageManagerImageSelectField(**defaults)
        return val

