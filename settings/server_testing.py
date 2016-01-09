from base import *
from os import environ

import dotenv
dotenv.read_dotenv()

TESTING = os.sys.argv[1:2] == ['test']


DOMAIN = '0.0.0.0:8000'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BROKER_URL = 'redis://localhost:6379/10'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/10'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_EVENT_SERIALIZER = 'pickle'

ES_DISABLED = True
