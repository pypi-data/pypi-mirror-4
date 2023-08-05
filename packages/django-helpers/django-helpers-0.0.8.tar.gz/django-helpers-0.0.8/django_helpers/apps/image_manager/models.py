from django.core.files.storage import get_storage_class
from django_helpers import get_settings_val, check_settings_val_exist

__author__ = 'ajumell'

from django.db import models
from django_helpers.forms.fields import ThumbnailImageField

check_settings_val_exist('MEDIA_ROOT')
check_settings_val_exist('MEDIA_URL')

STORAGE = get_storage_class(get_settings_val('IMAGE_MANAGER_STORAGE', None))
UPLOAD_TO = get_settings_val('IMAGE_MANAGER_FOLDER', 'image-manager/')

class Image(models.Model):
    name = models.SlugField(max_length=100, unique=True)
    alternate_text = models.CharField(max_length=255, blank=True)
    tooltip = models.CharField(max_length=255, blank=True)
    image = ThumbnailImageField(upload_to=UPLOAD_TO, storage=STORAGE())

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return self.image.url

    @property
    def thumbnail(self):
        return self.image.thumbnail


class ImageGroup(models.Model):
    name = models.SlugField(max_length=255)
    images = models.ManyToManyField(Image)


    def __unicode__(self):
        return self.name