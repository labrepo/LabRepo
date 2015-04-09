from __future__ import absolute_import

from os import environ

from .base import *


# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

import dotenv
dotenv.read_dotenv()


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

DEBUG = True

DOMAIN = environ.get('DOMAIN', 'localhost')

ALLOWED_HOSTS = [DOMAIN]

ADMINS = (
    ('Admin', environ.get('ADMIN_EMAIL')),
)

LANGUAGE_CODE = environ.get('LANGUAGE_CODE')

SOCIAL_AUTH_FACEBOOK_KEY = environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
#Google section
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
#Linkedin section
SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = environ.get('SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY')
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = environ.get('SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET')

_MONGODB_USER = environ.get('MONGODB_USER')
_MONGODB_PASSWD = environ.get('MONGODB_PASSWD')
_MONGODB_NAME = environ.get('MONGODB_NAME')
_MONGODB_HOST = environ.get('MONGODB_HOST')
_MONGODB_PORT = environ.get('MONGODB_PORT')


_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s:%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_PORT, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST, tz_aware=USE_TZ)

BROKER_URL = _MONGODB_DATABASE_HOST

CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": _MONGODB_HOST,
    "port": _MONGODB_PORT,
    'user': _MONGODB_USER,
    'password': _MONGODB_PASSWD,
    'database': _MONGODB_NAME,
    'taskmeta_collection': 'celery_tasks',
}
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_EVENT_SERIALIZER = 'pickle'
CELERY_RESULT_BACKEND = "mongodb"

BROKER_BACKEND = "mongodb"
BROKER_HOST = _MONGODB_HOST
BROKER_PORT = _MONGODB_PORT
BROKER_USER = _MONGODB_USER
BROKER_PASSWORD = _MONGODB_PASSWD
BROKER_VHOST = "celery"

EMAIL_HOST = get_env_setting('EMAIL_HOST')
EMAIL_PORT = get_env_setting('EMAIL_PORT')
EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = get_env_setting('EMAIL_USE_TLS')
