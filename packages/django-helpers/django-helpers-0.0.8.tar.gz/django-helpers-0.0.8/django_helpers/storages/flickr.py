from django.core.cache import cache

__author__ = 'ajumell'

import httplib

from urlparse import urlparse
from django.core.files.storage import Storage
from django.conf import settings
from flickrapi import FlickrAPI, IllegalArgumentException
from flickrapi.multipart import Part, Multipart
from flickrapi import make_utf8

IMAGE_TYPES = {
    'square': 'Square',
    'thumbnail': 'Thumbnail',
    'small': 'Small',
    'medium': 'Medium',
    'large': 'Large'
}

IMAGE_TYPES_PRIORITY = ['Square', 'Thumbnail', 'Small', 'Medium', 'Large']

class FlickrAPIHack(FlickrAPI):
    def __init__(self, api_key, secret=None, username=None,
                 token=None, format='etree', store_token=True, cache=False):
        FlickrAPI.__init__(self, api_key, secret, username, token, format, store_token, cache)

    def _FlickrAPI__upload_to_form(self, form_url, filename, file_obj, callback, **kwargs):
        """Can upload a file using file object"""

        if not filename:
            raise IllegalArgumentException("filename must be specified")
        if not self.token_cache.token:
            raise IllegalArgumentException("Authentication is required")

        format = self._FlickrAPI__extract_upload_response_format(kwargs)

        # Update the arguments with the ones the user won't have to supply
        arguments = {
            'auth_token': self.token_cache.token,
            'api_key': self.api_key
        }

        arguments.update(kwargs)

        # Convert to UTF-8 if an argument is an Unicode string
        kwargs = make_utf8(arguments)

        if self.secret:
            kwargs["api_sig"] = self.sign(kwargs)
        url = "http://%s%s" % (FlickrAPI.flickr_host, form_url)

        # construct POST data
        body = Multipart()

        for arg, value in kwargs.iteritems():
            part = Part({'name': arg}, value)
            body.attach(part)

        content = file_obj.read()
        file_obj.close()

        filepart = Part({'name': 'photo', 'filename': filename}, content, 'image/jpeg')
        body.attach(filepart)

        return self._FlickrAPI__wrap_in_parser(self._FlickrAPI__send_multipart, format,
            url, body, callback)

    def upload(self, filename, callback=None, **kwargs):
        raise Exception("Use upload_file method.")


    def upload_file(self, filename, file_obj, callback=None, **kwargs):
        return self._FlickrAPI__upload_to_form(FlickrAPI.flickr_upload_form, filename, file_obj, callback, **kwargs)


class FlickrStorageException(Exception):
    pass


class FlickrStorage(Storage):
    def __init__(self, options=None):
        self.options = {
            'cache': True,
        }

        self.options.update(options or settings.FLICKR_STORAGE_OPTIONS)
        self.flickr = FlickrAPIHack(self.options['api_key'],
            self.options['api_secret'],
            self.options['username'],
            self.options['token'],
            cache=self.options['cache'])

        if self.options['cache']:
            self.flickr.cache = cache

        (self.token, frob) = self.flickr.get_token_part_one(perms='delete')
        #TODO: move to management command
        if not self.token:
            raw_input('Press Enter...')

        self.flickr.get_token_part_two((self.token, frob))

    def _check_response(self, resp):
        if resp.attrib['stat'] != 'ok':
            err = resp.find('err')
            raise FlickrStorageException, "Error %s: %s" % (err.attrib['code'], err.attrib['msg'])

    def delete(self, name):
        resp = self.flickr.photos_delete(photo_id=name)

    def size(self, name):
        url = self.url(name)
        u = urlparse(url)
        conn = httplib.HTTPConnection(u.hostname)
        conn.request('HEAD', u.path)
        resp = conn.getresponse()
        return int(resp.getheader('content-length'))

    def _save(self, name, content):
        content.seek(0)             #ImageField read first 1024 bytes
        name = name.encode('utf-8')
        resp = self.flickr.upload_file(name, content.file)
        self._check_response(resp)
        name = resp.find('photoid').text
        content.close()
        return name

    def exists(self, name):
        return False

    def url(self, name, img_type=None):
        resp = self.flickr.photos_getSizes(photo_id=name)
        self._check_response(resp)
        value = ""
        prev_rank = -1
        for size in resp.findall('sizes/size'):
            label = size.attrib['label']
            if IMAGE_TYPES_PRIORITY.count(label) > 0:
                rank = IMAGE_TYPES_PRIORITY.index(label)
                if rank > prev_rank:
                    value = size.attrib['source']
                    prev_rank = rank
        return value

    def thumbnail(self, name):
        return self.get_size(name, 'Thumbnail')

    def get_size(self, name, image_size, resp=None):
        if resp is None:
            resp = self.flickr.photos_getSizes(photo_id=name)
            self._check_response(resp)

        for size in resp.findall('sizes/size'):
            label = size.attrib['label']
            if label == image_size:
                return size.attrib['source']
        return ""
