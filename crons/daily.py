#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

from fabric.api import *
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leech_devel.settings")
from django.conf import settings


def run_cron_jobs():
    with lcd(settings.BASE_DIR):
        local(settings.VIRTUALENV_PYTHON_PATH + ' manage.py process_daily_click_count')


if __name__ == '__main__':
    run_cron_jobs()