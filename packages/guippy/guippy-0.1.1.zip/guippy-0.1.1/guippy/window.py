#-*- coding: utf-8 -*-
"""For window procedures.
"""
from .api import GetForegroundWindow, FindWindowEx, SetForegroundWindow, \
    GetWindowRect, GW_CHILD, GW_ENABLEDPOPUP, GetWindow, OpenIcon, ShowWindow,\
    SW_SHOWMAXIMIZED, CloseWindow
from .shortcut import Normalizer
from .decorator import interval
from .error import Timeout

from ctypes.wintypes import RECT
import ctypes
import time
TIMEOUT = 5

class Window(object):
    def __init__(self, cname=None, wname=None):
        self.hwnd = None
        self.cname = cname
        self.wname = wname

    @staticmethod
    def get_window(cname=None, wname=None, timeout=TIMEOUT):
        func = None
        args = None
        if cname == wname == None:
            func = GetForegroundWindow
            args = []
        else:
            func = FindWindowEx
            args = [None, None, cname, wname]
        
        count_generator = None
        if timeout == 0:
            count_generator = itertools.count
        else:
            count_generator = lambda : xrange(timeout)

        for ii in count_generator():
            try:
                hwnd = func(*args)
                if hwnd:
                    return hwnd
            except WindowsError, err:
                pass
            time.sleep(1)
        raise Timeout
         
    def catch(self, cname=None, wname=None):
        """Search window handle for cname and wname."""
        self.cname = cname
        self.wname = wname
        self.hwnd = self.get_window(cname, wname)

    @interval
    def active(self):
        SetForegroundWindow(self.hwnd)

    def move(self):
        pass

    def close(self):
        pass
    
    def get_rect(self, normalize=True):
        rect = RECT()
        lprect = ctypes.pointer(rect)
        GetWindowRect(self.hwnd, lprect)
        if normalize:
            rect.left = Normalizer.xx(rect.left)
            rect.right = Normalizer.xx(rect.right)
            rect.top = Normalizer.yy(rect.top)
            rect.bottom = Normalizer.yy(rect.bottom)
        return rect

    def set_rect(self):
        pass

    def width(self):
        pass

    def height(self):
        pass

    def restore(self):
        self.minimize()
        OpenIcon(self.hwnd)
        self.active()
        time.sleep(1)
    
    def maximize(self):
        ShowWindow(self.hwnd, SW_SHOWMAXIMIZED)
        time.sleep(1)

    def minimize(self):
        CloseWindow(self.hwnd)
        time.sleep(1)

    def get_popup(self):
        child = Window()
        child.hwnd = GetWindow(self.hwnd, GW_ENABLEDPOPUP)
        return child

    def get_child(self):
        child = Window()
        child.hwnd = GetWindow(self.hwnd, GW_CHILD)
        return child


