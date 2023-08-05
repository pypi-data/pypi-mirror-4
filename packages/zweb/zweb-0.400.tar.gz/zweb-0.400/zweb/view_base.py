#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import urllib
import urlparse
from server._tornado import web
import css, js

from misc.config.render import render 
from model._db import mc

RENDER_KWDS = {
    'css':css,
    'js':js
}

class View(web.RequestHandler):
    def decode_argument(self, value, name=None):
        return value

    def on_finish(self):
        mc.reset()
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


class LoginView(View):
    def prepare(self):
        super(LoginView, self).prepare()
        if not self.current_user:
            _next_redirect(self, "/auth/login")


def _next_redirect(self, url):
    if self._finished:
        return
    
    next_url = self.request.uri

    if url and next_url and not next_url.startswith(url) and next_url.startswith("/") and len(next_url)>1:
        url += '?' + urllib.urlencode(dict(next=next_url))
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


