__author__ = 'ajumell'

from django.conf import settings
import tweepy

HasAuth = False

def auth():
    global HasAuth

    # TODO: Check auth using tweepy
    if HasAuth:
        return

    consumer_key = getattr(settings, 'TWITTER_CONSUMER_KEY', "")
    consumer_secret = getattr(settings, 'TWITTER_CONSUMER_SECRET', "")

    token = getattr(settings, 'TWITTER_TOKEN', "")
    secret = getattr(settings, 'TWITTER_SECRET', "")

    # TODO: Validation

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(token, secret)

    tweepy.API(auth)

    HasAuth = True



def get_public_tweets(username):
    return tweepy.api.user_timeline(username)



def send_direct_message(username, contents):
    auth()
    tweepy.api.send_direct_message(screen_name=username, text=contents)

def tweet(contents):
    auth()
    tweepy.api.update_status(contents)

def tweet_page(link):
    auth()
    # TODO: Complete
