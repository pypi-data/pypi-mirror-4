#-*- coding: utf-8 -*-
"""Graphical User Interfaces Procedures for PYthon.

 The guippy emulate various operations of computer users. It provides the
ability for emulate keyboards, mouses, window system, and clipboards. By using
this, you can run your computer automatically.

 This is a Pyhon 3rd party library. Written in pure Python. You need to Python
programming, but it is very easy to use. And you can easily and safely install.

example.

   >>> import guippy
   >>> gp = guippy.Guippy()
   >>> gp.catch()
   >>> gp.punch()


Let's get started.
"""
__version__ = '0.1.1'
__author__ = 'tak.esxima'
__credits__ = (__author__, )

import mouse
import keyboard
import window
import clipboard
import api
import error
import shortcut
import application
from .guippy import *  # import all objects in guippy.
from .mouse import Mouse
from .keyboard import Keyboard
from .window import Window
from .clipboard import Clipboard


__all__ = (
    # in guippy module
    'Guippy',
    # in other modules
    'mouse', 'keyboard', 'window', 'clipboard',
    'Mouse', 'Keyboard', 'Window', 'Clipboard',
    'api', 'error', 'shortcut', 'application',
    )

