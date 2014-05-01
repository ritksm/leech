"""
Django settings for leech_devel project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from . import local_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

TEMPLATE_DEBUG = local_settings.TEMPLATE_DEBUG

ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS


# Application definition

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
]

INTERNAL_APPS = [
    'leech',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'leech_devel.urls'

WSGI_APPLICATION = 'leech_devel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = local_settings.DATABASES

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = local_settings.LANGUAGE_CODE

TIME_ZONE = local_settings.TIME_ZONE

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = local_settings.STATIC_URL
STATIC_ROOT = local_settings.STATIC_ROOT

MEDIA_URL = local_settings.MEDIA_URL
MEDIA_ROOT = local_settings.MEDIA_ROOT

REDIS_HOST = local_settings.REDIS_HOST

REDIS_SHORTEN_URL_NAME = 'leech:url:{slug}'

REDIS_CLICK_COUNT_NAME = 'leech:url:click:{slug}'

REDIS_STAT_LOG_NAME = 'leech:url:stat:logs'

COOKIE_NAME_FOR_UUID = 'leech_user'

HOST = local_settings.HOST

REDIRECT_BASE_URL = HOST + '/go/'

STATISTIC_BASE_URL = HOST + '/stat/'

API_CLICK_COUNT_BASE_URL = HOST + '/api/click_count/'

HASH_ID_SALT = local_settings.HASH_ID_SALT
HASH_ID_MIN_LENGTH = 3

VIRTUALENV_PYTHON_PATH = local_settings.VIRTUALENV_PYTHON_PATH