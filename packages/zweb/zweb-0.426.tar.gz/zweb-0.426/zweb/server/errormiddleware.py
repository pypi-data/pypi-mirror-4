#!/usr/bin/env python
#coding:utf-8
import sys
from traceback import format_exc
import logging
from tornado.web import HTTPError, httplib

def ErrorMiddleware(application, render, template):
    def _(environ, start_response):
        try:
            return application(environ, start_response)
        except HTTPError, e:
            status_code = e.status_code

            log_message = e.log_message
            start_response(
                '%s %s'%(status_code, httplib.responses[status_code]),
                [('content-type', 'text/html')]
            )
            return [render(
                template,
                status_code=status_code,
                log_message=str(e)
            )]
        except:
            exc_info = sys.exc_info()
            traceback = format_exc()
            start_response(
                '500 Internal Server Error',
                [('content-type', 'text/html')],
                exc_info
            )
            logging.error(environ)
            logging.error(traceback)
            return [render(
                template,
                status_code=500,
                exc_info=exc_info,
                traceback=traceback,
                environ=environ,
            )]
    return _
