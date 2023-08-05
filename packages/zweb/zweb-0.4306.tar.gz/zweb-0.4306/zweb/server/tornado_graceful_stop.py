#coding:utf-8
import sys
import logging
import socket
import tornado 
import tornado.ioloop
import signal
import time
from tornado.netutil import bind_sockets
from tornado.httpserver import HTTPServer

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3
_server = None


def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def shutdown():
    global _server 
    logging.info('Stopping http server')
    _server.stop() # 不接收新的 HTTP 请求

    logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()

        if now < deadline:
            if io_loop._callbacks:
                io_loop.add_timeout(now + 1, stop_loop)
                return

        io_loop.stop() # 处理完现有的 callback 和 timeout 后，可以跳出 io_loop.start() 里的循环
        logging.info('Shutdown')

    stop_loop()


def server(port, application):
#    if IPV4_ONLY:
    sockets = bind_sockets(port, family=socket.AF_INET)
#    else:
#        sockets = bind_sockets(port)

    global _server 
    _server = HTTPServer(application, xheaders=True)
    _server.add_sockets(sockets)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    tornado.ioloop.IOLoop.instance().start()
    logging.info('Exit')

if __name__ == '__main__':
    pass
