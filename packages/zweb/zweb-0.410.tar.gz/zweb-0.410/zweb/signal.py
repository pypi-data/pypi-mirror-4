#coding:utf-8
from model._db import celery
from misc.config import HOST

class Signal(object):
    def __init__(self, name):
        self._sync = []
        self._async = []

        @celery.task(name=name)
        def _(*args):
            for func in self._async:
                func(*args)

        self.task = _.delay  

    def send(self, *args):
        for func in self._sync:
            func(*args) 
        if self._async:
            self.task(*args)

    def __call__(self, func):
        self._sync.append(func)
        return func

    def delay(self, func):
        self._async.append(func)
        return func


class _(object):
    def __getattr__(self, name):
        d = self.__dict__
        if name not in d:
            d[name] = Signal("%s.%s"%(HOST,name))
        return d[name]
        

SIGNAL = _()

if __name__ == "__main__":


    @SIGNAL.follow_new
    def _follow_new(a,b):
        print a,b 
   
    @SIGNAL.follow_new.delay
    def _follow_new(a, b):
        print a,b
    SIGNAL.follow_new.send(1 , 3)

