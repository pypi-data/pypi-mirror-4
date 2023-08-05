#!/usr/bin/env python
# -*- coding: utf-8 -*-

def attrcache(f):
    name = f.__name__
    @property
    def _attrcache(self):
        d = self.__dict__
        if name in d:
            return d[name]
        result = f(self)
        d[name] = result
        return result

    return _attrcache

