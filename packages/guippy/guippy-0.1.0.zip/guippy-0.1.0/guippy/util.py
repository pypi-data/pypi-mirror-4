#-*- coding: utf-8 -*-
"""This utility may use other modules.

 What has been defined here, does not depend on this package.
"""
import os

class Enum(object):
    """like to use enum of C.
x    """

    DEFAULT_INCREMENT = lambda x: x+1

    def __init__(self, default=0, increment=None):
        self.cur = default # current value
        self.increment = increment\
            if increment is not None else lambda x: x+1
#self.DEFAULT_INCREMENT
    
    def next(self, value=None, increment=None):
        if value is not None:
            self.cur = value
            
        if increment is not None:
            self.increment = increment

        cur = self.cur
        self.cur = self.increment(self.cur)
        return cur

enum = lambda *args, **kwds: Enum(*args, **kwds).next

_MD = enum() # mkdir return code
class Mkdir(object):
    """Make a directory."""
    SUCCESS = _MD() 
    FAIL = _MD()    

    @classmethod
    def p(cls, path):
        """like to use "mkdir -p"
        """
        try:
            os.makedirs(path)
        except (IOError, OSError, WindowsError), err:
            return cls.FAIL
        else:
            return cls.SUCCESS
del _MD

mkdir = Mkdir 
              
