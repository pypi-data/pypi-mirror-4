import re
from urllib2 import quote

from django import template
from django.utils.safestring import mark_safe
from django_helpers.helpers.social.twitter import get_public_tweets
from django_helpers.helpers.templatetags import parse_args, TemplateNode, create_context_from_kwargs
from django_helpers.helpers.views import render_to_string

register = template.Library()

__author__ = 'ajumell'

class TwitterTweetsNode(template.Node):
    def __init__(self, username):
        self.username = username

    def render(self, context):
        username = self.username.resolve(context, True)
        tweets = get_public_tweets(username)
        return render_to_string('tags/social/twitter.html',{
            'tweets': tweets
        })

@register.tag
def tweets(parser, token):
    bits = token.contents.split()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'%s' tag at least takes one arguments" % bits[0])
    value = parser.compile_filter(bits[1])
    return TwitterTweetsNode(value)


username_re = re.compile('[@]+([A-Za-z0-9_]+)')
hash_re = re.compile('[#]+([A-Za-z0-9_]+)')
link_re = re.compile(r"(http://[^ ]+)")

@register.filter
def format_tweet(value):
    value = link_re.sub(r'<a href="\1">\1</a>', value)
    value = hash_re.sub(r'<a href="http://search.twitter.com/search?q=\1">#\1</a>', value)
    value = username_re.sub(r'<a href="http://twitter.com/\1">@\1</a>', value)
    return mark_safe(value)

format_tweet.si_safe = True

class FacebookLikeButtonNode(TemplateNode):

    def render(self, context):
        args = self.args
        kwargs = self.kwarg
        cntxt = {}

        if len(args) != 0:
            url = args[1]
        elif kwargs.has_key('url'):
            url = kwargs['url']
        else:
            for c in context:
                print c
            url = context.get('current_full_url')

        if not url:
            raise template.TemplateSyntaxError("URL is no provided.")

        cntxt['url'] = quote(url)
        names = ['height', 'width', 'scheme', 'font']
        create_context_from_kwargs(kwargs, cntxt, names, context)
        return render_to_string('tags/social/facebook-like.html',cntxt)

@register.tag
def facebook_like(parser, token):
    bits = token.contents.split()
    args, kwargs = parse_args(bits, parser)
    return FacebookLikeButtonNode(args, kwargs)

