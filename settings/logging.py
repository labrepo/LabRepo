#  Logging settings for production using

from os import environ
from .base import INSTALLED_APPS

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'WARNING',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'django': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/default.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'simple'
        },
        'django_request': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_request.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'simple'
        },
        'app_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'simple'
        },
        'celery_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/celery.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'simple'
        },
        'elastic_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/elastic.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django'],
            'propagate': True,
            'level': 'WARNING',
        },
        'django.request': {
            'handlers': ['django_request'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['celery_handler'],
            'level': 'WARNING',
            'propagate': True,
        },
        'celery.worker': {
            'handlers': ['celery_handler'],
            'level': 'WARNING',
            'propagate': True,
        },
        'elasticsearch': {
            'handlers': ['elastic_handler'],
            'level': 'WARNING',
        },
        'apps': {
            'handlers': ['app_handler'],
            'level': 'WARNING',
        },
        'labrepo': {
            'handlers': ['app_handler'],
            'level': 'WARNING',
        },
    }
}


SENTRY_DSN = environ.get('SENTRY_DSN', None)

if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )

    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }
    LOGGING['handlers']['sentry'] = {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }
    for key, logger, in LOGGING['loggers'].items():
        logger['handlers'].append('sentry')