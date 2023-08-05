from django_helpers.apps.image_manager.fields import ImageManagerImageField
from django_helpers.apps.supersized import TransitionChoices
from django.db import models

__author__ = 'ajumell'

class SuperSizedSlider(models.Model):
    name = models.CharField(max_length=75, unique=True)
    autoplay = models.BooleanField(default=True)
    fit_always = models.BooleanField(default=False)
    fit_landscape = models.BooleanField(default=False)
    fit_portrait = models.BooleanField(default=True)
    horizontal_center = models.BooleanField(default=False)
    image_protect = models.BooleanField(default=True)
    keyboard_nav = models.BooleanField(default=True)
    min_height = models.IntegerField(default=0)
    min_width = models.IntegerField(default=0)
    new_window = models.BooleanField(default=True)
    pause_hover = models.BooleanField(default=False)
    performance = models.IntegerField(default=1)
    random = models.BooleanField(default=False)
    slideshow = models.BooleanField(default=True)
    slide_interval = models.IntegerField(default=5000)
    slide_links = models.BooleanField(default=False)
    start_slide = models.IntegerField(default=1)
    stop_loop = models.BooleanField(default=False)
    thumb_links = models.BooleanField(default=True)
    thumbnail_navigation = models.BooleanField(default=True)
    transition = models.CharField(default='fade', choices=TransitionChoices, max_length=25)
    transition_speed = models.IntegerField(default=750)
    vertical_center = models.BooleanField(default=True)
    progress_bar = models.BooleanField(default=True)
    mouse_scrub = models.BooleanField(default=True)
    show_thumbnails = models.BooleanField(default=False)
    hide_controls = models.BooleanField(default=False)


    def slides(self):
        return self.supersizedslide_set.all()


    def __unicode__(self):
        return self.name


class SuperSizedSlide(models.Model):
    slider = models.ForeignKey(SuperSizedSlider)
    image = ImageManagerImageField()
    caption = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)

    def __unicode__(self):
        return "%d - %s" % (self.id, self.image.name)
