from django.db import models
from django_helpers.apps.image_manager.fields import ImageManagerImageField
from django_helpers.apps.nivo_slider import EffectsChoices, ThemesChoices


__author__ = 'ajumell'

class NivoSlider(models.Model):
    name = models.CharField(max_length=32, unique=True)
    effect = models.CharField(max_length=75, choices=EffectsChoices)
    slices = models.SmallIntegerField(default=15)

    box_cols = models.SmallIntegerField(default=8)
    box_rows = models.SmallIntegerField(default=4)

    animation_speed = models.SmallIntegerField(default=700)
    pause_time = models.SmallIntegerField(default=3000)

    direction_nav = models.BooleanField(default=True)
    control_nav = models.BooleanField(default=True)
    control_bav_thumbs = models.BooleanField(default=False)
    pause_on_hover = models.BooleanField(default=True)
    manual_advance = models.BooleanField(default=False)

    prev_text = models.CharField(max_length=32, default='Prev')
    next_text = models.CharField(max_length=32, default='Next')

    random_start = models.BooleanField(default=False)
    theme_name = models.CharField(max_length=75, default='bar', choices=ThemesChoices)

    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)


    def slides(self):
        return self.nivosliderslide_set.all()


    def __unicode__(self):
        return self.name


class NivoSliderSlide(models.Model):
    slider = models.ForeignKey(NivoSlider)
    image = ImageManagerImageField()
    link = models.URLField(blank=True)
    caption = models.CharField(max_length=255, blank=True)
    transition = models.CharField(max_length=75, choices=EffectsChoices, blank=True)

    @property
    def alternate_text(self):
        return self.image.alternate_text

    def __unicode__(self):
        return "%d - %s" % (self.id, self.image.name)