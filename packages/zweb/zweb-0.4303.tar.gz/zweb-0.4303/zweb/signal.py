#coding:utf-8

from misc.config import HOST
from types import FunctionType
from model._db import celery
from model._celery import SIGNAL_IMPORT
import atexit


def call(func, args):
    if type(func) is FunctionType:
        args = args[:func.func_code.co_argcount]
    func(*args)

class Signal(object):
    _DELAY = []
    
    def __init__(self, name):
        self._sync = []
        self._async = []
        self.name = name

        @celery.task(name="%s.%s"%(HOST,name))
        def _(*args):
            for func in self._async:
                call(func,args)

        self._delay = _.delay  

    # SINGAL.xxxxxx.rm(func)
    def rm(self, func):
        if func in self._sync:
            self._sync.remove(func) 
        if func in self._async:
            self._async.remove(func) 

    @classmethod
    def send_delay(cls):
        for func, args in cls._DELAY: 
            func(*args)
        cls._DELAY = []

    def send(self, *args):
        name = self.name
        if name in SIGNAL_IMPORT:
            for i in SIGNAL_IMPORT[name]:
                __import__(i)
            del SIGNAL_IMPORT[name]

        for func in self._sync:
            call(func,args)

        if self._async:
            self._DELAY.append((self._delay, args)) 

    def __call__(self, func):
        self._sync.append(func)
        return func

    def delay(self, func):
        self._async.append(func)
        return func

atexit.register(Signal.send_delay)


class _(object):
    def __getattr__(self, name):
        d = self.__dict__
        if name not in d:
            d[name] = Signal(name)
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
    SIGNAL.send_delay()

