#coding:utf-8
import traceback

def _route_chain(view, args):
    handlers = []
    for i in args:
        prefix = i.__name__

        #import view.blog._install
        try:
            __import__('%s.%s'%(prefix,view))
        except ImportError, e:
            traceback.print_exc() 
            raise e
        i = __import__(prefix, globals(), locals(), ['_route'], -1)
        handlers.extend(i._route.route.handlers)

    return handlers

def app_install(application, view, app_list):
    for domain , route_list in app_list:
        if not domain.startswith("."):
            domain = domain.replace('.', r"\.")
        application.add_handlers(
            domain,
            _route_chain(view, route_list)
        )

