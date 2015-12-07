"""
Django settings for lab project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import djcelery

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _


djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def rel(*x):
    return os.path.join(BASE_DIR, *x)

os.sys.path.append(rel('apps'))

ADMINS = (
    ('Admin', 'admin@example.com'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lq(3)t1@+4$t#jzzpwi5rf)))kf^(49e%is&*!_7asbrtxae9z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

DOMAIN = 'localhost:8000'

ALLOWED_HOSTS = [DOMAIN]

# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'user@example.com'
# EMAIL_HOST_PASSWORD = 'paSSworD'
# EMAIL_USE_TLS = True

SERVER_EMAIL = DEFAULT_FROM_EMAIL = 'info@example.com'
# Application definition

DEFAULT_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'ckeditor',
    'reversion',
    'django_forms_bootstrap',
    'djcelery',
    'rosetta',
    'registration',
    'social.apps.django_app.default',
    'widget_tweaks',
    'rest_framework',
)
LOCAL_APPS = (
    'comments',
    'common',
    'experiments',
    'filemanager',
    'history',
    'labs',
    'measurements',
    'dashboard',
    'profiles',
    'search',
    'tags',
    # 'unit_collections',
    'units',
    'uploader',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'units.middleware.DisableCSRF'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
           os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'common.context_processors.menu_processor',
                'common.context_processors.sidebar_processor',
                'common.context_processors.js_variables_processor',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
                'django.template.context_processors.request',
            ],
        },
    },
]

ROOT_URLCONF = 'common.urls'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 'django.db.backends.dummy',
        'NAME': rel('lab.sqlite3'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static/"),
)

STATIC_URL = '/static/'

STATIC_ROOT = rel('public', 'static')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

MEDIA_URL = '/media/'

MEDIA_ROOT = rel('public', 'media')

# SOCIAL_AUTH_STORAGE = 'social.apps.django_app.me.models.DjangoStorage'

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
# SOCIAL_AUTH_FACEBOOK_KEY = '460569577381739'
# SOCIAL_AUTH_FACEBOOK_SECRET = 'b0231a0b9344c98c7f85d67c10ccf32b'

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '766010577484-9657jjre4728h3glefl3om0thc3ulj4o.apps.googleusercontent.com'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '4IVfUGcHfZjjSfuUxE5taUvV'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email']
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True

# SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = '757bs6iu6r66ta'
# SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = 'dsVAOq7B4o7iid4o'
SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_basicprofile', 'r_emailaddress']
SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ['email-address']


AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookAppOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.linkedin.LinkedinOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL = 'profiles.LabUser'

# registration
ACCOUNT_ACTIVATION_DAYS = 1

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = reverse_lazy('login_auth')
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)
LOCALE_PATHS = (
    rel('conf', 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATETIME_INPUT_FORMATS = (
    '%m/%d/%Y %H:%M',
)

ES_URLS = ['http://localhost:9200']
ES_INDEXES = {'default': 'lab_index'}
ES_DISABLED = False

FILEMANAGER_UPLOAD_ROOT = MEDIA_ROOT + '/uploads/'
FILEMANAGER_UPLOAD_URL = MEDIA_URL + 'uploads/'
FILEMANAGER_AUTH_CALLBACK = 'filemanager.auth.allow_in_lab'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'Pillow'
CKEDITOR_CONFIGS = {
    'ckeditor': {
        'toolbar': [
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Bold', 'Italic',
             'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'Smiley', 'SpecialChar', 'Blockquote'],
            ['TextColor', 'BGColor', 'Styles', 'Format', 'Font', 'FontSize'],
            ['Source'],
        ],
        'width': '100%',
        'height': 200,
        'skin': 'bootstrapck',
    },
    'comments': {
        'toolbar': [
            ['Link', 'Unlink'],
            ['Image', 'Table', 'Smiley', 'SpecialChar', 'Blockquote'],
            ['Source'],
        ],
        'width': '100%',
        'height': 100,
        'skin': 'bootstrapck',
    },
}
