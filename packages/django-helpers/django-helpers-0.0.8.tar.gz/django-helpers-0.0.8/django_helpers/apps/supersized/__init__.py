"""

0 or 'none' - No transition effect
1 or 'fade' - Fade effect (Default)
2 or 'slideTop' - Slide in from top
3 or 'slideRight' - Slide in from right
4 or 'slideBottom' - Slide in from bottom
5 or 'slideLeft' - Slide in from left
6 or 'carouselRight' - Carousel from right to left
7 or 'carouselLeft' - Carousel from left to right


"""
from django_helpers import create_attr_from_obj, get_settings_val
from django_helpers.helpers.views import render_to_string
from django_helpers.templatetags.static_manger import add_js_file, add_jquery, add_css_file, add_jquery_easing

__author__ = 'ajumell'

class SuperSizedTransitions(object):
    none = 'none'
    fade = 'fade'
    slideTop = 'slideTop'
    slideRight = 'slideRight'
    slideLeft = 'slideLeft'
    slideBottom = 'slideBottom'
    carouselRight = 'carouselRight'
    carouselLeft = 'carouselLeft'

TransitionChoices = []

for item in dir(SuperSizedTransitions):
    if not item.startswith('__'):
        val = getattr(SuperSizedTransitions, item)
        if TransitionChoices.count(val) == 0:
            TransitionChoices.append((item, val))


class SuperSized(object):
    autoplay = True
    fit_always = False
    fit_landscape = False
    fit_portrait = True
    horizontal_center = False
    image_protect = True
    keyboard_nav = True
    min_height = 0
    min_width = 0
    new_window = True
    pause_hover = False
    performance = 1
    random = False
    slideshow = True
    slide_interval = 5000
    slide_links = False
    start_slide = 1
    stop_loop = False
    thumb_links = True
    thumbnail_navigation = True
    transition = SuperSizedTransitions.fade
    transition_speed = 750
    vertical_center = True
    progress_bar = True
    mouse_scrub = True

    show_thumbnails = False
    hide_controls = False


    def __init__(self):
        add_jquery()
        add_jquery_easing()

        add_js_file('super-sized/js/supersized.3.2.7.min.js')
        add_js_file('super-sized/theme/supersized.shutter.min.js')

        add_css_file('super-sized/css/supersized.css')
        add_css_file('super-sized/theme/supersized.shutter.css')
        self._slides = []

    def add_slide(self, image, title, thumb, link):
        if not thumb:
            thumb = image

        self._slides.append({
            'image': image,
            'title': title,
            'thumb': thumb,
            'url': link
        })


    def render(self):
        attrs = create_attr_from_obj(self)
        attrs['slides'] = self._slides
        attrs['show_thumbnails'] = self.show_thumbnails
        attrs['hide_controls'] = self.hide_controls
        attrs['STATIC_URL'] = get_settings_val('STATIC_URL', '')
        return render_to_string('super-sized.html', attrs)

    def __unicode__(self):
        return self.render()

    def __str__(self):
        return self.render()

