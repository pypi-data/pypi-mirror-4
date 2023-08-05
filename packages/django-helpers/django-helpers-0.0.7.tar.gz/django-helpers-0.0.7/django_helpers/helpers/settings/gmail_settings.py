"""
    This file has the settings for sending email from gmail.
    just import * from this file and start sending mails.

    Requirements:
    GMAIL_USERNAME Environmental Variable
    GMAIL_PASSWORD Environmental Variable

    Usage:
    from django_helpers.helpers.settings.gmail_settings import *
"""

__author__ = 'ajumell'

from os import environ

def has_gmail():
    return environ.has_key('GMAIL_USERNAME') and environ.has_key('GMAIL_PASSWORD')

if has_gmail():
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = environ.get('GMAIL_USERNAME')
    EMAIL_HOST_PASSWORD = environ.get('GMAIL_PASSWORD')