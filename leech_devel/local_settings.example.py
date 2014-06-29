#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'very secret key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

STATIC_URL = '/static/'
STATIC_ROOT = ''

MEDIA_URL = '/media/'
MEDIA_ROOT = ''

REDIS_HOST = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

HOST = 'http://localhost:8000'

HASH_ID_SALT = 'hash salt'

VIRTUALENV_PYTHON_PATH = '/opt/virtualenv/leech/bin/python'

PRIVATE_SITE = True
REGISTER_OPEN = True