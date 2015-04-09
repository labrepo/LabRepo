from base import *

DEBUG = True

DOMAIN = environ.get('DOMAIN', 'localhost')

ALLOWED_HOSTS = [DOMAIN]

_MONGODB_USER = 'webmaster'
_MONGODB_PASSWD = 'webmaster'
_MONGODB_NAME = 'labrepo'
_MONGODB_HOST = '127.0.0.1'
_MONGODB_PORT = 27017


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
