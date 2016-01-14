from __future__ import absolute_import

from os import environ, urandom

from django.core.exceptions import ImproperlyConfigured

from .base import *



import dotenv
dotenv.read_dotenv()

TESTING = os.sys.argv[1:2] == ['test']
if TESTING:
    raise SystemExit('Use a testing settings file')


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

DEBUG = False

SECRET_KEY = environ.get('SECRET_KEY', urandom(32))

DOMAIN = environ.get('DOMAIN', 'localhost')

ALLOWED_HOSTS = [DOMAIN]

ADMINS = (
    ('Admin', environ.get('ADMIN_EMAIL')),
)

LANGUAGE_CODE = environ.get('LANGUAGE_CODE', LANGUAGE_CODE)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ.get('POSTGRESQL_DBNAME'),
        'USER': environ.get('POSTGRESQL_USER'),
        'PASSWORD': environ.get('POSTGRESQL_PASSWORD'),
        'HOST': environ.get('POSTGRESQL_HOST'),
        'PORT': environ.get('POSTGRESQL_PORT'),
    }
}


#Facebook section
SOCIAL_AUTH_FACEBOOK_KEY = environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
#Google section
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
#Linkedin section
SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = environ.get('SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY')
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = environ.get('SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET')


EMAIL_HOST = get_env_setting('EMAIL_HOST')
EMAIL_PORT = get_env_setting('EMAIL_PORT')
EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = get_env_setting('EMAIL_USE_TLS')
SERVER_EMAIL = DEFAULT_FROM_EMAIL = get_env_setting('SERVER_EMAIL')

from  .logging import *