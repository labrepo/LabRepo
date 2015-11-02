from base import *
from os import environ

import dotenv
dotenv.read_dotenv()

TESTING = os.sys.argv[1:2] == ['test']


DOMAIN = '0.0.0.0:8000'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


_MONGODB_NAME = environ.get('MONGODB_TEST_DATABASE')

_MONGODB_USER = environ.get('MONGODB_USER')
_MONGODB_PASSWD = environ.get('MONGODB_PASSWD')
_MONGODB_HOST = environ.get('MONGODB_HOST')
_MONGODB_PORT = environ.get('MONGODB_PORT')

# TEST_RUNNER = 'django_selenium.selenium_runner.SeleniumTestRunner'
# SELENIUM_DRIVER = 'Firefox'
# SELENIUM_DRIVER_TIMEOUT = 10

_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s:%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_PORT, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST, tz_aware=USE_TZ)


BROKER_URL = 'redis://localhost:6379/10'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/10'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_EVENT_SERIALIZER = 'pickle'

ES_DISABLED = True

if TESTING and 'test' not in _MONGODB_NAME:
    raise SystemExit('Wrong mongo db?')
