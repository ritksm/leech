#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import time
import json
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'leech_devel.settings'
from django.conf import settings
import tornado.gen
import tornado.ioloop
import tornado.web
import tornadoredis

c = tornadoredis.Client(settings.REDIS_HOST['host'], settings.REDIS_HOST['port'])
c.connect()


class RedirectHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, slug):
        redis_name = settings.REDIS_SHORTEN_URL_NAME.format(slug=slug)
        stat_redis_name = settings.REDIS_STAT_LOG_NAME
        key_exists = yield tornado.gen.Task(c.exists, redis_name)
        if key_exists:
            redirect_url = yield tornado.gen.Task(c.get, redis_name)

            yield tornado.gen.Task(c.lpush, stat_redis_name, json.dumps(
                {'user-agent': self.request.headers.get('User-Agent', ''),
                 'timestamp': time.time(),
                 'ip': self.request.remote_ip,
                 'slug': slug}
            ).encode('utf8'))
            self.redirect(redirect_url)
        else:
            self.write('error')
            self.finish()

application = tornado.web.Application([
    (r'/(\w+)', RedirectHandler)
])

if __name__ == '__main__':
    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()