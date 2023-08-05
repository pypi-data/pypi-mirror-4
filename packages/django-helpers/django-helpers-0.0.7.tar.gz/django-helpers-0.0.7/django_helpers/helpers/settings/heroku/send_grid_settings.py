"""
    This file has the settings for sending sms from send grid add-on
    of heroku. just import * from this file and start sending mails.
"""
from os import environ

def has_send_grid():
    return environ.has_key('SENDGRID_USERNAME') and environ.has_key('SENDGRID_PASSWORD')

if has_send_grid():
    EMAIL_PORT = 587
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = environ.get('SENDGRID_USERNAME')
    EMAIL_HOST_PASSWORD = environ.get('SENDGRID_PASSWORD')
    EMAIL_USE_TLS = False