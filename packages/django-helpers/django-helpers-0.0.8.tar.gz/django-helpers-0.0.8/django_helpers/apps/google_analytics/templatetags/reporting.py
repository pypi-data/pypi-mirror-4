__author__ = 'ajumell'

import datetime
import gdata.analytics.client
import gdata.sample_util
import gdata.service

from django.conf import settings

LAST_UPDATED = {}
CACHE = {}

CLIENT = None

def get_last_updated(app, id):
    date = LAST_UPDATED.get(app)
    if date is None:
        date = {}
        LAST_UPDATED[app] = date
    return date.get(id)


def set_last_updated(app, id, val):
    date = LAST_UPDATED.get(app)
    if date is None:
        date = {}
        LAST_UPDATED[app] = date
    date[id] = val


def get_cache(app, id):
    date = CACHE.get(app)
    if date is None:
        date = {}
        CACHE[app] = date
    return date[id]


def set_cache(app, id, val):
    date = CACHE.get(app)
    if date is None:
        date = {}
        CACHE[app] = date
    date[id] = val

# TODO: Need more settings options

def get_feed(query):
    global CLIENT
    if CLIENT is None:
        SOURCE_APP_NAME = 'Xeoscript Daily Analytics Application'
        my_client = gdata.analytics.client.AnalyticsClient()
        my_client.client_login(settings.GMAIL_USERNAME, settings.GMAIL_PASSWORD, SOURCE_APP_NAME,
            my_client.auth_service)
        CLIENT = my_client
    return CLIENT.GetDataFeed(query)

def get_metric(app_id, id):
    today = datetime.date.today()
    if today == get_last_updated(app_id, id):
        val = get_cache(app_id, id)
        if val:
            return val
    else:
        set_last_updated(app_id, id, today)

    print 'Collecting info from google...'

    start = datetime.date.today() - datetime.timedelta(years=10)
    data_query = gdata.analytics.client.DataFeedQuery({
        'ids': 'ga:%d' % id,
        'start-date': start,
        'end-date': today,
        'metrics': 'ga:%s' % app_id,
        'sort': 'ga:visits',
        'max-results': '1000'})

    feed = get_feed(data_query)
    val = feed.aggregates.metric[0].value
    set_cache(app_id, id, val)
    return val

def get_page_visits(id):
    app_id = "visits"
    return get_metric(app_id, id)


