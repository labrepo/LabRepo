from __future__ import absolute_import

from os import environ

from .base import *


# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

import dotenv
dotenv.read_dotenv()

TESTING = os.sys.argv[1:2] == ['test']
if TESTING:
    raise SystemExit('Use testing settings file')

def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

DEBUG = False

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

BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_EVENT_SERIALIZER = 'pickle'


EMAIL_HOST = get_env_setting('EMAIL_HOST')
EMAIL_PORT = get_env_setting('EMAIL_PORT')
EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = get_env_setting('EMAIL_USE_TLS')
SERVER_EMAIL = DEFAULT_FROM_EMAIL = get_env_setting('SERVER_EMAIL')

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)
RAVEN_CONFIG = {
    'dsn': 'http://8a1b0be8fed541faaa200632186abe84:e98212790f1844b6aecb980d0b37d920@sentry.magic60.ru/3',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 'django': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': 'logs/default.log',
        #     'maxBytes': 1024*1024*5, # 5 MB
        #     'backupCount': 5,
        # },
        # 'request_handler': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': 'logs/django_request.log',
        #     'maxBytes': 1024*1024*20, # 20 MB
        #     'backupCount': 5,
        # },
        # 'app_handler': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': 'logs/app.log',
        #     'maxBytes': 1024*1024*20, # 20 MB
        #     'backupCount': 5,
        # },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['sentry'],
            'propagate': True,
            'level': 'WARNING',
        },
        'django.request': {
            'handlers': ['sentry'],
            'level': 'ERROR',
            'propagate': False,
        },
        'app': {
            'handlers': ['sentry'],
            'level': 'WARNING',
        },
    }
}
