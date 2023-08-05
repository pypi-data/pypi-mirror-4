#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import urllib
import urlparse
from server._tornado import web
import css, js

from misc.config.render import render
from misc.config import HOST 
from model._db import mc
from signal import SIGNAL, Signal
from zweb.sentry import CLIENT

RENDER_KWDS = {
    'css':css,
    'js':js
}

class View(web.RequestHandler):
    def decode_argument(self, value, name=None):
        return value

    def prepare(self):
        mc.reset()

    def on_finish(self):
        Signal.send_delay()
        #print "mc_reset"

    def render(self, template_name=None, **kwds):
        if template_name is None:
            if not hasattr(self, 'template'):
                mod = self.__module__[5:]
                self.template = '/%s/%s.html' % (
                    mod.replace(".","/"),
                    self.__class__.__name__
                )
            template_name = self.template

        current_user = self.current_user
        kwds['current_user'] = current_user
        kwds['current_user_id'] = self.current_user_id
        kwds['request'] = self.request
        kwds['this'] = self
        kwds['_xsrf'] = self._xsrf
        kwds.update(RENDER_KWDS)
        if not self._finished:
            self.finish(render(template_name, **kwds))
    
    @property
    def current_user_id(self):
        if not hasattr(self, '_current_user_id'):
            current_user = self.current_user
            if current_user:
                self._current_user_id = current_user.id
            else:
                self._current_user_id = 0
        return self._current_user_id


    def get_current_user(self):
        return None

    @property
    def _xsrf(self):
        return '_xsrf=%s'%self.xsrf_token

if CLIENT:
    def write_error(self, status_code, **kwargs):
        """Override implementation to report all exceptions to sentry"""
        data['exc_info']=kwargs.get('exc_info','')
        rv = super(View, self).write_error(status_code, **kwargs)
        data = {
            'sentry.interfaces.Http': {
                'url':  self.request.full_url(),
                'method': self.request.method,
                'data': self.request.arguments,
                'query_string': self.request.query,
                'cookies': self.request.headers.get('Cookie', None),
                'headers': dict(self.request.headers),
            }
        }

        data['current_user_id'] = self.current_user_id
        CLIENT.capture('Exception', data=data, **kwargs)
        return rv 


    View.write_error = write_error 

class LoginView(View):
    def prepare(self):
        super(LoginView, self).prepare()
        user_id = self.current_user_id
        if user_id:
            SIGNAL.login_view.send(user_id)
        if not self.current_user:
            _next_redirect(self, "//%s/auth/login"%HOST)


def _next_redirect(self, url):
    if self._finished:
        return
    
    request = self.request
    next_url = request.uri

    if url and next_url and not next_url.startswith(url) and next_url.startswith("/") and len(next_url)>1:
        back = request.protocol + "://" + request.host + request.uri
        url += '?' + urllib.urlencode(dict(next=back))
    self.redirect(url)
    return True


class NoLoginView(View):
    def prepare(self):
        super(NoLoginView, self).prepare()
        if self._finished:
            return
        if self.current_user:
            return self.redirect("/")
    
class JsonLoginView(View):
    def prepare(self):
        super(JsonLoginView, self).prepare()
        if self._finished:
            return
        if not self.current_user:
            self.finish({"login":1})


