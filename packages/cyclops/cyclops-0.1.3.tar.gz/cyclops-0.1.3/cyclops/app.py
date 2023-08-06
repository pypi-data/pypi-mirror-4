#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from Queue import Queue

import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.web import url
from torndb import Connection

from cyclops.handlers.router import RouterHandler, CountHandler
from cyclops.handlers.healthcheck import HealthCheckHandler
from cyclops.tasks import ProjectsUpdateTask, SendToSentryTask


def configure_app(self, config=None, log_level='INFO', debug=False, main_loop=None):
    self.config = config
    self.main_loop = main_loop

    handlers = [
        url(r'/api/(?P<project_id>\d+)/store/', RouterHandler, name="router"),
        url(r'/count', CountHandler, name="count"),
        url(r'/healthcheck(?:/|\.html)?', HealthCheckHandler, name="healthcheck"),
    ]

    logging.info("Connecting to db on {0}:{1} on database {2} with user {3}".format(
        self.config.MYSQL_HOST,
        self.config.MYSQL_PORT,
        self.config.MYSQL_DB,
        self.config.MYSQL_USER)
    )

    self.db = Connection(
        "%s:%s" % (self.config.MYSQL_HOST, self.config.MYSQL_PORT),
        self.config.MYSQL_DB,
        user=self.config.MYSQL_USER,
        password=self.config.MYSQL_PASS
    )

    options = {
    }

    self.project_keys = {}
    self.items_to_process = Queue()

    projects_update_task = ProjectsUpdateTask(self, self.main_loop)
    projects_update_task.update()
    projects_update_task.start()

    send_to_sentry_task = SendToSentryTask(self, self.main_loop)
    send_to_sentry_task.update()
    send_to_sentry_task.start()

    if debug:
        options['debug'] = True
        config.NUMBER_OF_FORKS = 1

    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    return handlers, options


class CyclopsApp(tornado.web.Application):

    def __init__(self, config=None, log_level='INFO', debug=False, main_loop=None):
        handlers, options = configure_app(self, config, log_level, debug, main_loop)
        super(CyclopsApp, self).__init__(handlers, **options)
