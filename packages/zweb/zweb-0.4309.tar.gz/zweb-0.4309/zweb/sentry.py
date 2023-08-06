#!/usr/bin/env python
#coding:utf-8



from raven import Client
from decorator import decorator


class Sentry(object):
    def __init__(self, client):
        self._client = client
        if client:
            @decorator
            def _(func, *args, **kwds):
                try:
                    return func(*args, **kwds)
                except:
                    client.captureException()
                    raise
        else:
            def _(func):
                return func
        self._call = _ 

    def __call__(self, func):
        return self._call(func)
 
