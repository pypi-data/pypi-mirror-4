#coding:utf-8
import _env
import misc.config
import misc.config.dev

from zweb.server.server_cherry import WSGIServer
from online import run

run.wsgi_server = WSGIServer




if __name__ == "__main__":
    from zweb.reloader.reload_server import auto_reload
    auto_reload(run)
    


