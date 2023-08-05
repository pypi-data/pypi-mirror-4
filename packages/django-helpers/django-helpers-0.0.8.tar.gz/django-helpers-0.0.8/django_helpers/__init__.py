import collections
from django.conf.urls import include, url
from urls import urlpatterns

def add_app_url(name, urls):
    reg_exp = r'^%s/' % name
    name += '-urls'

    for pattern in urlpatterns:
        if pattern._regex == reg_exp:
            print 'url already exist.'
            return

    pattern = url(reg_exp, include(urls), name=name)
    urlpatterns.append(pattern)
    print 'URL added:', name


def get_settings_val(name, default=None):
    from django.conf import settings

    obj = getattr(settings, name, default)
    return obj


def check_settings_val_exist(name, tolerate_blank=False, tolerate_spaces=True):
    val = get_settings_val(name)
    if val is None:
        raise Exception('Missing settings value: %s' % name)

    if (not tolerate_blank and val) == '' or (not tolerate_spaces and val.isspace()):
        raise Exception('Improperly configured settings value: %s' % name)


def is_func(obj):
    return hasattr(obj, '__call__')


def is_list(obj):
    if isinstance(obj, basestring):
        return False
    return isinstance(obj, collections.Sequence)


def convert_js_bool(o):
    if o:
        return 'true'
    return 'false'


def create_attr_from_obj(obj, ignore_function=True, ignore_lists=True, js_bool=True):
    attrs = dir(obj)
    d = {}
    for attr in attrs:
        val = getattr(obj, attr)
        if ignore_function and is_func(val):
            continue

        if ignore_lists and is_list(val):
            continue

        if val is True or val is False:
            val = convert_js_bool(val)

        d[attr] = val

    return d

