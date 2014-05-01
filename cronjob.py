#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

from fabric.api import *
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leech_devel.settings")
from django.conf import settings


def run_cron_jobs():
    with lcd(settings.BASE_DIR):
        local(settings.VIRTUALENV_PYTHON_PATH + ' manage.py process_stat_logs')


if __name__ == '__main__':
    run_cron_jobs()