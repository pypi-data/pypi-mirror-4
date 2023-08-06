# -*- coding: utf-8 -*-
import _env
import tornado.wsgi
from misc.config import DEBUG

application = tornado.wsgi.WSGIApplication(
    login_url='/auth/login' ,
    xsrf_cookies=True,
    debug=DEBUG
)

from app_install import APP_INSTALL 
from zweb.app_install import app_install
app_install(application, APP_INSTALL)
 
