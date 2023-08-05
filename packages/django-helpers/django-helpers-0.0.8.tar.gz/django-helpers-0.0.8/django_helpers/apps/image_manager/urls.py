from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='image-manager-home'),
    url(r'^delete/(?P<image_id>\d+)-(?P<image_slug>.+)/$', views.delete_image, name='image-manager-delete-image'),
)
