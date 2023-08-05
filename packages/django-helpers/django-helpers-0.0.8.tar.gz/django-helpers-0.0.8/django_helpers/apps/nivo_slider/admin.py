__author__ = 'ajumell'

from django.contrib.admin import site, ModelAdmin
from models import NivoSlider, NivoSliderSlide

class NivoSliderAdmin(ModelAdmin):
    pass

site.register(NivoSlider)
site.register(NivoSliderSlide)

