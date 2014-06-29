#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import json
import uuid
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from leech.models import *
import threading
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils.decorators import method_decorator
from leech.utils import login_required_for_private_site


class IndexView(TemplateView):
    """ index view
    """

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            slugs = ShortenUrl.objects.get_by_user(user=self.request.user)
        else:
            user_uuid = self.request.COOKIES.get(settings.COOKIE_NAME_FOR_UUID, None)
            if user_uuid:
                slugs = ShortenUrl.objects.get_by_uuid(user_uuid=user_uuid)
            else:
                slugs = []

        context['slugs'] = slugs
        context['redirect_base_url'] = settings.REDIRECT_BASE_URL
        context['stat_base_url'] = settings.STATISTIC_BASE_URL

        return context

    @method_decorator(login_required_for_private_site)
    def get(self, request, *args, **kwargs):

        response = super(IndexView, self).get(request, *args, **kwargs)
        # set uuid cookie
        if not settings.COOKIE_NAME_FOR_UUID in self.request.COOKIES.keys():
            response.set_cookie(settings.COOKIE_NAME_FOR_UUID, uuid.uuid4(), max_age=31536000)

        return response


class GenerateView(View):
    """ generate slug from source_url
    """

    @method_decorator(login_required_for_private_site)
    def post(self, request):
        source_url = request.POST.get('url', '')
        if not source_url:
            return HttpResponseBadRequest()

        if not settings.COOKIE_NAME_FOR_UUID in self.request.COOKIES.keys():
            user_uuid = uuid.uuid4()
        else:
            user_uuid = request.COOKIES.get(settings.COOKIE_NAME_FOR_UUID)

        if request.user.is_authenticated():
            # associate url with user
            ShortenUrl.objects.shorten_url(url=source_url, user=request.user)
        else:
            # associate url with user_uuid when user is not authenticated
            ShortenUrl.objects.shorten_url(url=source_url, user_uuid=user_uuid)

        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie(settings.COOKIE_NAME_FOR_UUID, user_uuid, max_age=31536000)

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
        shorten_url = ShortenUrl.objects.filter(slug=self.slug)
        if not shorten_url.exists():
            return
        else:
            shorten_url = shorten_url[0]

        shorten_url.click()

        ClickLog.objects.create_log(shorten_url,
                                    self.request.META.get('HTTP_USER_AGENT'),
                                    self._get_client_ip())


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


class APIGenerateView(View):
    """ generate shorten url by calling api
    """

    def post(self, request):
        source_url = request.POST.get('url', '')
        if not source_url:
            return HttpResponseBadRequest()

        shorten_url = ShortenUrl.objects.shorten_url(url=source_url)

        return HttpResponse(json.dumps({'link': ''.join([settings.REDIRECT_BASE_URL, shorten_url.slug]),
                                        'slug': shorten_url.slug,
                                        'count': ''.join([settings.API_CLICK_COUNT_BASE_URL, shorten_url.slug])}),
                            content_type='application/json')

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(APIGenerateView, self).dispatch(request, *args, **kwargs)


class RemarksEditView(View):
    """ edit url remarks
    """

    @method_decorator(login_required_for_private_site)
    def post(self, request):
        slug_id = request.POST.get('pk', None)
        remarks = request.POST.get('remarks', None)

        if slug_id and remarks:
            url = ShortenUrl.objects.filter(pk=int(slug_id))
            if url.exists():
                url = url[0]
                url.remarks = remarks
                url.save()

        return HttpResponseRedirect('/')


class APIClickCountView(View):
    """ get slug click count
    """

    def get(self, request, slug):
        shorten_url = ShortenUrl.objects.filter(slug=slug)
        if not shorten_url.exists():
            return HttpResponseBadRequest()

        return HttpResponse(json.dumps({'count': shorten_url[0].click_count()}), content_type='application/json')


class StatisticView(TemplateView):
    """ show statistic of shorten url
    """

    template_name = 'stat.html'

    def __init__(self):
        super(StatisticView, self).__init__()
        self.slug = None

    def get_context_data(self, **kwargs):
        context = super(StatisticView, self).get_context_data(**kwargs)

        shorten_url = ShortenUrl.objects.filter(slug=self.slug)
        if not shorten_url.exists():
            return HttpResponseBadRequest()
        else:
            shorten_url = shorten_url[0]

        context['click_logs'] = shorten_url.click_logs.all().order_by('-click_time')[:100]
        context['click_count'] = shorten_url.click_count()

        context['daily_click_counts_name'] = []
        context['daily_click_counts_count'] = []
        for count in reversed(shorten_url.get_recent_daily_click_counts()):
            context['daily_click_counts_name'].append(count.date.strftime('%Y-%m-%d'))
            context['daily_click_counts_count'].append(count.count)
        context['daily_click_counts_name'] = json.dumps(context['daily_click_counts_name'])
        context['daily_click_counts_count'] = json.dumps(context['daily_click_counts_count'])

        return context

    @method_decorator(login_required_for_private_site)
    def get(self, request, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        return super(StatisticView, self).get(request, *args, **kwargs)


class LoginView(TemplateView):
    """ user login view
    """

    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['next_url'] = self.request.GET.get('next')
        return context

    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            next_url = request.GET.get('next', '/')
            return HttpResponseRedirect(next_url)
        else:
            return super(LoginView, self).get(request, *args, **kwargs)
        
    def post(self, request):
        next_url = request.GET.get('next', None)
        if not next_url:
            next_url = '/'
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)

        return HttpResponseRedirect(next_url)


class LogoutView(View):
    """ user logout view
    """

    def get(self, request):
        if request.user.is_authenticated():
            auth.logout(request)

        return HttpResponseRedirect('/')


class RegisterView(View):
    """ user register view
    """

    def post(self, request):
        if not settings.REGISTER_OPEN:
            # register off
            return HttpResponse('<p>注册已关闭，请联系管理员。</p><a href="/">点击返回主页</a>')

        next_url = request.GET.get('next', None)
        if not next_url:
            next_url = '/'

        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        confirm_password = request.POST.get('confirm_password', None)

        if username and password and confirm_password and password == confirm_password:
            if not User.objects.filter(username=username):
                user = User.objects.create_user(username=username,
                                                password=password)
                if user:
                    auth.login(request, auth.authenticate(username=username, password=password))

        return HttpResponseRedirect(next_url)


__all__ = ['IndexView',
           'GenerateView',
           'SlugRedirectView',
           'APIGenerateView',
           'APIClickCountView',
           'StatisticView',
           'RemarksEditView',
           'LoginView',
           'LogoutView',
           'RegisterView', ]