#coding:utf-8
import _tornado
import tornado.ioloop
from tornado_graceful_stop import server

class Run(object):
    def __init__(self, port, application):
        self.port = port
        self.application = application

    def __call__(self):
        import sys
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
        else:
            port = self.port
            if type(port) in (list, tuple):
                port = port[0]


        server(port, self.application)

