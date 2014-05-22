#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import pytz
import datetime
import redis
from hashids import Hashids
from django.conf import settings
from django.db import models
from model_utils import Choices
import httpagentparser
from django.contrib.auth.models import User


class ShortenUrlManager(models.Manager):
    """ shorten url model manager
    """

    def shorten_url(self, url, user_uuid=None, user=None):
        """ Adds a long URL to the database
        """
        parse_result = urlparse(url)
        if not parse_result.scheme:
            # url scheme not provided, add 'http' as default
            url = ''.join(['http://', parse_result.netloc, parse_result.path,
                           parse_result.params, parse_result.query,
                           parse_result.fragment])

        shorten_url = super(ShortenUrlManager, self).create(source_url=url,
                                                            user_uuid=user_uuid,
                                                            user=user)
        slug = Hashids(salt=settings.HASH_ID_SALT,
                       min_length=settings.HASH_ID_MIN_LENGTH).encrypt(shorten_url.pk)
        shorten_url.slug = slug
        shorten_url.save()

        self._save_to_redis_cache(source_url=shorten_url.source_url, slug=shorten_url.slug)

        return shorten_url

    def get_by_uuid(self, user_uuid):
        return self.filter(user_uuid=user_uuid)

    def get_by_user(self, user):
        return self.filter(user=user)

    def get_source_url(self, slug):
        if not slug:
            return ''

        source_url = self._get_from_redis_cache(slug)
        if source_url:
            return source_url

        source_url = self.filter(slug=slug)
        if source_url.exists():
            source_url = source_url[0]
            self._save_to_redis_cache(source_url.source_url, source_url.slug)
            return source_url.source_url

    def _save_to_redis_cache(self, source_url, slug):
        """ save source_url,slug map to redis
        """
        name = settings.REDIS_SHORTEN_URL_NAME.format(slug=slug)
        redis_server = redis.Redis(**settings.REDIS_HOST)
        redis_server.set(name, source_url)

    def _get_from_redis_cache(self, slug):
        """ get source url from redis by slug
        """
        name = settings.REDIS_SHORTEN_URL_NAME.format(slug=slug)
        redis_server = redis.Redis(**settings.REDIS_HOST)
        if not redis_server.exists(name):
            return ''
        else:
            return redis_server.get(name)


class ShortenUrl(models.Model):
    """ shorten url model
    """
    objects = ShortenUrlManager()

    source_url = models.CharField(max_length=255, verbose_name='Source URL')
    slug = models.CharField(max_length=32, verbose_name='URL Slug', null=True)
    remarks = models.CharField(max_length=255, verbose_name='Remarks', blank=True, default='')
    create_time = models.DateTimeField(verbose_name='Create Time', auto_now_add=True)
    user_uuid = models.CharField(max_length=64, verbose_name='UUID', null=True)
    user = models.ForeignKey(User, verbose_name='User', related_name='urls', null=True)

    class Meta(object):
        app_label = 'leech'
        verbose_name = 'Shorten URL'
        verbose_name_plural = 'Shorten URL'

    def __repr__(self):
        return '<Shorten URL for "%s">' % self.source_url

    def __unicode__(self):
        return self.__repr__()

    def click(self):
        """ process the clicking
        """
        redis_server = redis.Redis(**settings.REDIS_HOST)
        redis_server.incr(settings.REDIS_CLICK_COUNT_NAME.format(slug=self.slug))  # increase click count

    def click_count(self):
        """ get click count from Redis
        """
        count = redis.Redis(**settings.REDIS_HOST).get(settings.REDIS_CLICK_COUNT_NAME.format(slug=self.slug))
        if not count:
            count = 0
        return int(count)

    def get_recent_daily_click_counts(self):
        return DailyClickCount.objects.filter(shorten_url=self).order_by('-date')[:7]


class ClickLogManager(models.Manager):
    """ url click log model manager
    """

    def create_log(self, shorten_url, user_agent, remote_address, click_time=None):
        if not click_time:
            click_time = datetime.datetime.now().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        click_log = super(ClickLogManager, self).create(shorten_url=shorten_url,
                                                        user_agent=user_agent,
                                                        remote_address=remote_address,
                                                        click_time=click_time)

        if click_log:
            # parse attributes from user-agent
            result = httpagentparser.detect(click_log.user_agent)
            os = result.get('os', {})
            browser = result.get('browser', {})
            dist = result.get('dist', {})

            attribute_type = ClickLogAttribute.ATTRIBUTE_TYPE

            click_log.set_attribute(attribute_type.os, os.get('name', 'Unknown'))
            click_log.set_attribute(attribute_type.browser, browser.get('name', 'Unknown'))
            click_log.set_attribute(attribute_type.browser_version, browser.get('version', 'Unknown'))
            click_log.set_attribute(attribute_type.distribution, dist.get('name', 'Unknown'))
            click_log.set_attribute(attribute_type.distribution_version, dist.get('name', 'Unknown'))

        return click_log

    def get_logs_by_slug(self, slug):
        return self.filter(shorten_url__slug=slug)

    def create_log_by_redis_log(self, log):
        user_agent = log['user-agent']
        remote_address = log['ip']
        shorten_url = ShortenUrl.objects.get(slug=log['slug'])
        click_time = datetime.datetime.fromtimestamp(log['timestamp']).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        log = self.create_log(shorten_url, user_agent, remote_address, click_time=click_time)

        if log:
            # click the url if created from redis log
            shorten_url.click()
        return log


class ClickLog(models.Model):
    """ url click log
    """
    objects = ClickLogManager()

    shorten_url = models.ForeignKey(ShortenUrl, verbose_name='Shorten URL', related_name='click_logs')
    user_agent = models.CharField(max_length=255, verbose_name='User Agent')
    remote_address = models.CharField(max_length=64, verbose_name='Remote Address')
    click_time = models.DateTimeField(verbose_name='Click Time')

    def set_attribute(self, name, value):
        return ClickLogAttribute.objects.create(click_log=self,
                                                name=name,
                                                value=value)

    def get_attribute(self, name):
        logs = ClickLogAttribute.objects.filter(click_log=self,
                                                name=name)
        if not logs.exists():
            return None
        else:
            return logs[0]

    class Meta(object):
        app_label = 'leech'
        verbose_name = 'Click Log'
        verbose_name_plural = 'Click Log'

    def __repr__(self):
        return '<Click Log for "%s">' % self.shorten_url.source_url

    def __unicode__(self):
        return self.__repr__()


class ClickLogAttribute(models.Model):
    """ click log attribute model
    """
    ATTRIBUTE_TYPE = Choices((0, 'os', 'Operating System'),
                             (1, 'browser', 'Browser'),
                             (2, 'browser_version', 'Browser Version'),
                             (3, 'distribution', 'Distribution'),
                             (4, 'distribution_version', 'Distribution Version'))

    click_log = models.ForeignKey(ClickLog, verbose_name='Click Log', related_name='attributes')
    name = models.IntegerField(verbose_name='Attribute Name', choices=ATTRIBUTE_TYPE)
    value = models.CharField(max_length=255, verbose_name='Attribute Value')

    class Meta(object):
        app_label = 'leech'
        verbose_name = 'Click Log Attribute'
        verbose_name_plural = 'Click Log Attribute'

    def __repr__(self):
        return 'Log %d: %s = %s' % (self.click_log.pk, self.name, self.value)

    def __unicode__(self):
        return self.__repr__()


class DailyClickCount(models.Model):
    """ daily click count model
    """

    shorten_url = models.ForeignKey(ShortenUrl, verbose_name='Shorten URL', related_name='daily_click_counts')
    date = models.DateField(verbose_name='Count Date')
    count = models.IntegerField(verbose_name='Click Count')

    class Meta(object):
        app_label = 'leech'
        verbose_name = 'Daily Click Count'
        verbose_name_plural = 'Daily Click Count'


__all__ = ['ShortenUrl',
           'ClickLog',
           'ClickLogAttribute',
           'DailyClickCount',
]