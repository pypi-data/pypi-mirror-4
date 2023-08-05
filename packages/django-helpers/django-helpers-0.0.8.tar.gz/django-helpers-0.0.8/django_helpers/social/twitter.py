__author__ = 'ajumell'

import tweepy

consumer_key = "2gSVq31o1icSftlDTrCRQ"
consumer_secret = "kNxG4EEHO9PG0Xvi4hgRjlQshKpqOcZdtlUM94MN8M"

token = "103590211-DHKjfZlL83WmVNb8TyfPLCZd8y9ieB6QNt6p3gRB"
secret = "mRscTV1O2H55aoL4b9pSnBup0DB3BTNGQTBho6BYks"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(token, secret)

api = tweepy.API(auth)
def post_tweet():
    x = api.update_status("My first tweet from my application")
    print x

def get_public_tweets():
    public_tweets = tweepy.api.user_timeline('ajumell')
    for tweet in public_tweets:
        print tweet.text
        print tweet.author
        print tweet.user
        user = tweet.user

        print user.name
        print user.screen_name
        print user.profile_image_url

        for x in dir(tweet):
            print x

def send_direct_message():
    api.send_direct_message(screen_name="sujiths777", text="Dude my first direct message from tweet app")


get_public_tweets()