#-*- coding: utf-8 -*-
"""This and that in order to control the mouses.
"""
from .api import mouse_event, GetCursorPos, ME_MOVE, ME_ABSOLUTE, ME_WHEEL, \
    ME_LEFTDOWN, ME_LEFTUP, ME_MIDDLEDOWN, ME_MIDDLEUP, ME_RIGHTDOWN, ME_RIGHTUP
from .shortcut import Normalizer 
from .decorator import interval

import ctypes
from ctypes.wintypes import POINT

LEFT, MIDDLE, RIGHT = range(3)
BUTTONDOWN_EVENT = {LEFT: ME_LEFTDOWN,
                    MIDDLE: ME_MIDDLEDOWN,
                    RIGHT: ME_RIGHTDOWN,
                    }

BUTTONUP_EVENT = {LEFT: ME_LEFTUP,
                  MIDDLE: ME_MIDDLEUP,
                  RIGHT: ME_RIGHTUP,
                  }

DEFAULT_ABSOLUTE = True
DEFAULT_NORMALIZE = True

def _mouse_event(code, xx=0, yy=0, wheel=0, flag=0):
    """I/F with mouse_event().
    
    It created for setting default value.
    """
    return mouse_event(code, xx, yy, wheel, flag)

def call_mouse_event(func):
    """A decorator to call the mouse_event().
    
     The return value of the method that has been decorated by it, is used as
    arguments to the mouse_event(). To passing arguments for mouse_event() is
    affected by the return value type of decorated method by it. Pass arguments
    to mouse_event() as variable length keyword arguments if that type is
    dictionary. Pass arguments to it as variable length non keyword arguments
    if that is list or tuple. Pass arguments to it as simple arguments if other
    than those. This behavior will be a problem when pass a dictionary or a list
    or a tuple as a arguments to mouse_event(). In that case, the return value of
    method decorated by it be must wrapping moreover to a list or tuple. But
    mouse_event() is reject arguments as list or tuple or dictionary. Behavior is
    not defined.
    """

    def _wrap(obj, *args, **kwds):
        call_args = func(obj, *args, **kwds)
        typ = type(call_args)
        if typ == dict:
            return _mouse_event(**call_args)
        elif typ in (list, tuple):
            return _mouse_event(*call_args)
        else:
            return _mouse_event(call_args)
    return _wrap

class Button(object):
    @classmethod
    @call_mouse_event
    def drag(cls, button=None):
        """Drag on the button of mouse.

         A variable button is id of mouse button. Be input object with
        LEFT or MIDDLE or RIGHT. If not exist id then raise KeyError.
        """
        button = LEFT if button is None else button
        return BUTTONDOWN_EVENT[button] # raise KeyError
    
    @classmethod
    @call_mouse_event
    def drop(cls, button=None):
        """Drop off the button of mouse.
        
         A variable button is id of mouse button. See drag().
        """
        button = LEFT if button is None else button
        return BUTTONUP_EVENT[button] # raise KeyError

    @classmethod
    def click(cls, button=None):
        """Click the mouse.
        
         A variable button is id of mouse button. See drag().
        """
        cls.drag(button)
        cls.drop(button)
    
    @classmethod
    def wclick(cls, button=None):
        """Double click the mouse.

         A variable button is id of mouse button. See drag().
        """
        for ii in range(2):
            cls.click(button)
        
    @classmethod
    def wheel(cls, num=1):
        """Wheel the mouse.
        
         A variable num is wheel count. The num greater than 0, TEMAE.
        The num less than 0, MUKOU.
        """
        return ME_WHEEL|ME_MOVE, 0, 0, num

class Position(object):
    """Control position of mouse pointer.
    """

    @classmethod
    @call_mouse_event
    def jump(cls, xx, yy,
             normalize=DEFAULT_NORMALIZE, absolute=DEFAULT_ABSOLUTE):
        """Moving mouse pointer.

         The xx and yy is coord. The normalize is coord normalize switch.
        The absolute is switch of to using absolute coord.
        """
        code = ME_MOVE
        if normalize:
            code |= ME_ABSOLUTE

        if normalize and not absolute:
            nowx, nowy = cls.now(normalize)
            xx += nowx
            yy += nowy
        elif not normalize and absolute:
            nowx, nowy = cls.now(normalize)
            xx = -nowx + xx
            yy = -nowy + yy
        return code, xx, yy

    @staticmethod
    def now(normalize=DEFAULT_NORMALIZE):
        """Getting now coord of mouse pointer.
        
         The normalize is switch of to using mormarize coord.
        """
        point = POINT()
        lppoint = ctypes.pointer(point)
        GetCursorPos(lppoint)
        if normalize:
            point = Normalizer.point(point)
        return point.x, point.y

class Mouse(Button, Position):
    """Combination button and position of mouse emulate.
    """
    
    @classmethod
    def point(cls, *args, **kwds):
        """Click after move the mouse pointer.
        """
        cls.jump(*args, **kwds)
        cls.click()

