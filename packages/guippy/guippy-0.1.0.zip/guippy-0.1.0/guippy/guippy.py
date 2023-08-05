#-*- coding: utf-8 -*-
from .mouse import Mouse
from .window import Window
from .keyboard import Keyboard
from .clipboard import Clipboard

class PedigreeGuippy(object):
    def __init__(self):
        self.ms = Mouse()
        self.cb = Clipboard()
        self.kbd = Keyboard()
        self.win = Window()

    def mark_line(self):
        self.click()
        self.kbd.home()
        self.kbg.shift(push=True, release=False)
        self.kbd.end()
        self.kbg.shift(push=False, release=True)

    def makr_all(self):
        self.click()
        self.kbd.page_up()
        self.kbd.home
        self.kbg.shift(push=True, release=False)
        self.kbd.page_down()
        self.kbd.end()
        self.kbg.shift(push=False, release=True)

    def chase(self, xx=0, yy=0, normalize=True):
        rect = self.win.get_rect(normalize)
        xx = Normalizer.xx(xx) + rect.left
        yy = Normalizer.yy(yy) + rect.top
        self.ms.move(xx, yy)
        
    def get_area(self):
        pass

    def get_line(self):
        pass

    def poweroff(self):
        pass

class HybridGuippy(PedigreeGuippy, Mouse, Keyboard, Window, Clipboard):
    def __init__(self):
        self.ms = self
        self.cb = self
        self.kbd = self
        self.win = self

Guippy = HybridGuippy
