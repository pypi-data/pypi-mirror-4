from django import forms
from django_helpers.apps.form_renderer import FormRenderer
from models import Image

__author__ = 'ajumell'


class AddImageForm(forms.ModelForm):
    class Meta:
        model = Image

class EditImageForm(forms.ModelForm):
    class Meta:
        model = Image
        exclude = ('image', )


class AddImageFormRenderer(FormRenderer):
    form_id = 'add-image-form'
    form_submit = 'Upload Image'
