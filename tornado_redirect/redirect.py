#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

import time
import json
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'leech_devel.settings'
from django.conf import settings as django_settings
import tornado.gen
import tornado.ioloop
import tornado.web
import tornadoredis
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

c = tornadoredis.Client(django_settings.REDIS_HOST['host'], django_settings.REDIS_HOST['port'])
c.connect()


class RedirectHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, slug):
        redis_name = django_settings.REDIS_SHORTEN_URL_NAME.format(slug=slug)
        stat_redis_name = django_settings.REDIS_STAT_LOG_NAME
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


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(\w+)', RedirectHandler)
        ]
        settings = {}
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()