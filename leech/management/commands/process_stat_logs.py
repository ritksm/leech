#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import json
from django.core.management.base import BaseCommand, CommandError
import redis
from django.conf import settings
from leech.models import ClickLog


class Command(BaseCommand):

    def handle(self, *args, **options):
        redis_server = redis.Redis(**settings.REDIS_HOST)
        log = redis_server.rpop(settings.REDIS_STAT_LOG_NAME)
        index = 0
        while log and index < 10000:
            # process 10000 logs per run or stop when the queue is empty
            index += 1
            try:
                ClickLog.objects.create_log_by_redis_log(json.loads(log.decode('utf8')))
            except:
                pass
            log = redis_server.rpop(settings.REDIS_STAT_LOG_NAME)