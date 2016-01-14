from base import *

TESTING = os.sys.argv[1:2] == ['test']
if TESTING:
    raise SystemExit('Use a testing settings file')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#DOMAIN = '127.0.0.1:8080'  # Set another value if a site isn't running on the localhost


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel('lab.sqlite3'),
    }
}

