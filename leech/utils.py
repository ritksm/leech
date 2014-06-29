#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME


def login_required_for_private_site(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    if settings.PRIVATE_SITE:
        return login_required(function, redirect_field_name, login_url)
    else:
        return function