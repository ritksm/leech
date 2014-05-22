#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import datetime
from django.core.management.base import BaseCommand
from leech.models import ClickLog, ShortenUrl, DailyClickCount


class Command(BaseCommand):

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        yesterday_start = datetime.datetime(year=yesterday.year,
                                            month=yesterday.month,
                                            day=yesterday.day,
                                            hour=0,
                                            minute=0,
                                            second=0)
        yesterday_end = datetime.datetime(year=now.year,
                                          month=now.month,
                                          day=now.day,
                                          hour=0,
                                          minute=0,
                                          second=0)

        for slug in ShortenUrl.objects.all():
            count = ClickLog.objects.filter(shorten_url=slug,
                                            click_time__gte=yesterday_start,
                                            click_time__lt=yesterday_end).count()

            if DailyClickCount.objects.filter(shorten_url=slug,
                                              date=yesterday).exists():
                DailyClickCount.objects.filter(shorten_url=slug,
                                               date=yesterday).update(count=count)
            else:
                DailyClickCount.objects.create(shorten_url=slug,
                                               date=yesterday,
                                               count=count)
