#-*- coding: utf-8 -*-
import api

import ctypes


class Display:
    XMAX = api.GetSystemMetrics(api.SM_CXSCREEN)
    YMAX = api.GetSystemMetrics(api.SM_CYSCREEN)
    
class Normalizer(object):
    COEF_X = 0xFFFF/float(Display.XMAX)
    COEF_Y = 0xFFFF/float(Display.YMAX)
    
    @classmethod
    def xx(cls, value):
        return int(value * cls.COEF_X)

    @classmethod
    def yy(cls, value):
        return int(value * cls.COEF_Y)

    @classmethod
    def rect(cls, rect):
        rect.left = cls.xx(rect.left)
        rect.right = cls.xx(rect.right)
        rect.top = cls.yy(rect.top)
        rect.bottom = cls.yy(rect.bottom)
        return rect

    @classmethod
    def point(cls, _point):
        _point.x = cls.xx(_point.x)
        _point.y = cls.yy(_point.y)
        return _point
        
class Denormalizer(Normalizer):
    @classmethod
    def xx(cls, value):
        rc = int(float(value)/cls.COEF_X)
        if rc != 0:
            unity = rc/abs(rc)
            rc += unity
        return rc
    @classmethod
    def yy(cls, value):
        rc = int(float(value)/cls.COEF_Y)
        if rc != 0:
            unity = rc/abs(rc)
            rc += unity
        return rc
    
def get_window_handle(cname=None, wname=None, timeout=10, interval=1):
    func, args = None, None
    if cname == wname == None:
        func = api.GetForegroundWindow
        args = []
    else:
        func = api.FindWindowEx
        args = [None, None, str(cname), str(wname)]
    
    for ii in range(timeout/interval):
        try:
            hwnd = func(*args)
            if hwnd:
                return hwnd
        except Windowserror, err:
            pass
        time.sleep(interval)
    raise TimeoutError()

def get_window_rect(hwnd, absolute=True):
    rect = api.RECT()
    lprect = ctypes.pointer(rect)
    api.GetWindowRect(hwnd, lprect)
    if absolute:
        rect = Normalize.rect(rect)
    return rect

