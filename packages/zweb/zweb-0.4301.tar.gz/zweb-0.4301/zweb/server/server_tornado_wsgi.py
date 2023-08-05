#!/usr/bin/env python
#coding:utf-8

import _tornado


from misc import config
from misc.config.render import render

from errormiddleware import ErrorMiddleware

import tornado.httpserver
import tornado.ioloop
from tornado.wsgi import WSGIContainer
import _webob_fix
from tornado_graceful_stop import server

def WSGIServer(port, application):
    application = ErrorMiddleware(application, render, '_error.html')
    container = WSGIContainer(application)

    server(port, container)




class Run(object):
    def __init__(self, port, application, wsgi_server=WSGIServer):
        self.port = port
        self.application = application
        self.wsgi_server = wsgi_server

    def __call__(self):
        import sys
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
        else:
            port = self.port
            if type(port) in (list, tuple):
                port = port[0]

        print 'server on port %s'%port

        self.wsgi_server(port, self.application)


