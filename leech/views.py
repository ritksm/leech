#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import uuid
from django.conf import settings
from django.views.generic import TemplateView, View
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from leech.models import *
import json
import threading
import httpagentparser


def _encode_cookie_json_data(data):
    return json.dumps(data)


def _decode_cookie_json_data(cookie_data):
    return json.loads(cookie_data)


class IndexView(TemplateView):
    """ index view
    """

    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        user_uuid = self.request.COOKIES.get(settings.COOKIE_NAME_FOR_UUID, None)
        if user_uuid:
            slugs = ShortenUrl.objects.get_by_uuid(user_uuid=user_uuid)
        else:
            slugs = []

        context['slugs'] = slugs
        context['redirect_base_url'] = settings.REDIRECT_BASE_URL
        context['stat_base_url'] = settings.STATISTIC_BASE_URL

        return context

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)
        # set uuid cookie
        if not settings.COOKIE_NAME_FOR_UUID in self.request.COOKIES.keys():
            response.set_cookie(settings.COOKIE_NAME_FOR_UUID, uuid.uuid4())

        return response


class GenerateView(View):
    """ generate slug from source_url
    """

    def post(self, request):
        source_url = request.POST.get('url', '')
        if not source_url:
            return HttpResponseBadRequest()

        if not settings.COOKIE_NAME_FOR_UUID in self.request.COOKIES.keys():
            user_uuid = uuid.uuid4()
        else:
            user_uuid = request.COOKIES.get(settings.COOKIE_NAME_FOR_UUID)

        shorten_url = ShortenUrl.objects.shorten_url(url=source_url, user_uuid=user_uuid)

        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie(settings.COOKIE_NAME_FOR_UUID, user_uuid)

        return response


class RedirectLoggerThread(threading.Thread):
    """ log redirect request in another thread
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.slug = kwargs.pop('slug')
        super(RedirectLoggerThread, self).__init__(*args, **kwargs)

    def _get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def run(self):
        click_log = ClickLog.objects.create_log(self.slug,
                                                self.request.META.get('HTTP_USER_AGENT'),
                                                self._get_client_ip())
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


class SlugRedirectView(View):
    """ redirect to source_url by slug
    """

    def get(self, request, slug):
        result = ShortenUrl.objects.get_source_url(slug)
        if not result:
            return HttpResponseRedirect(reverse('index'))
        else:
            log_thread = RedirectLoggerThread(slug=slug, request=request)
            log_thread.start()
            return HttpResponseRedirect(result)


__all__ = ['IndexView',
           'GenerateView',
           'SlugRedirectView',]