import os
import sys
import json
import errno

def ensure_directory(path):
    try:
        os.makedirs(path)
    except OSError, os_error:
        if os_error.errno != errno.EEXIST:
            raise
    return path

PROJECT_ROOT = ensure_directory(os.path.expanduser('~/.djangopypi2'))
USER_SETTINGS_FILE = os.path.join(PROJECT_ROOT, 'settings.json')

USER_SETTINGS_DEFAULTS = dict(
    ADMINS        = [],
    DEBUG         = False,
    TIME_ZONE     = 'America/Chicago',
    WEB_ROOT      = '/',
    LANGUAGE_CODE = 'en-us',
)

if not os.path.exists(USER_SETTINGS_FILE):
    user_settings_file = open(USER_SETTINGS_FILE, 'w')
    user_settings_file.write(json.dumps(USER_SETTINGS_DEFAULTS, indent=4))
    user_settings_file.close()

USER_SETTINGS = json.loads(open(USER_SETTINGS_FILE, 'r').read())

DEBUG = USER_SETTINGS['DEBUG']
TEMPLATE_DEBUG = DEBUG

ADMINS = USER_SETTINGS['ADMINS']
TIME_ZONE = USER_SETTINGS['TIME_ZONE']
LANGUAGE_CODE = USER_SETTINGS['LANGUAGE_CODE']

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
    }
}

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = ensure_directory(os.path.join(PROJECT_ROOT, 'media'))
MEDIA_URL = USER_SETTINGS['WEB_ROOT'].rstrip('/') + '/media/'

STATIC_ROOT = ensure_directory(os.path.join(PROJECT_ROOT, 'static'))
STATIC_URL = USER_SETTINGS['WEB_ROOT'].rstrip('/') + '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'qf!u&amp;+fb+m4g@z8=#^v4du0)&amp;51z0e@_j+5tyw)w9=f20a6wr*'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'djangopypi2.website.urls'

WSGI_APPLICATION = 'djangopypi2.website.wsgi.application'

LOGIN_URL = '/users/login/'
LOGOUT_URL = '/users/logout/'
LOGIN_REDIRECT_URL = '/'

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'djangopypi2.apps.pypi_ui',
    'djangopypi2.apps.pypi_users',
    'djangopypi2.apps.pypi_manage',
    'djangopypi2.apps.pypi_metadata',
    'djangopypi2.apps.pypi_packages',
    'djangopypi2.apps.pypi_frontend',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
