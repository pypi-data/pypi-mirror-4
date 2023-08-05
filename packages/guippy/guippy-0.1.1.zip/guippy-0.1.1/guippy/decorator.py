#-*- coding: utf-8 -*-
import time

INTERVAL = 0.02

def interval(func, sec=INTERVAL):
    def _wrap(self, *args, **kwds):
        rc = func(self, *args, **kwds)
        time.sleep(sec)
        return rc
    return _wrap

def specialkey(func):
    def _wrap(cls, message):
        code = func(cls)
        cls.key(code, push=True, pull=False) # push key
        cls.punch(message)
        cls.key(code, push=False, pull=True) # pull key
    return _wrap


