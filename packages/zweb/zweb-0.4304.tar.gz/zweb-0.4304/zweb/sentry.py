#!/usr/bin/env python
#coding:utf-8



from raven import Client
from misc.config import SENTRY
from decorator import decorator

if SENTRY:
    CLIENT = Client(SENTRY)

    @decorator
    def sentry(func, *args, **kwds):
        try:
            return func(*args, **kwds)
        except:
            CLIENT.captureException()
            raise
else:
    CLIENT = None
    def sentry(func):
        return func


