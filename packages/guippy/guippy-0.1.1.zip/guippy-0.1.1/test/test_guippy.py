#! /usr/bin/env python
#-*- coding: utf-8 -*-
import startup
import guippy
from guippy.error import Timeout

import time
import string
import random
import unittest
from unittest import TestCase

# test
area = lambda target, base, width=10: (base-width) <= target <= (base+width)

LOOP_MAX = 0xFFF
ASCII_CHARS = string.letters + string.digits + string.punctuation

class GuippyTest(TestCase):
    NOTEPAD = u'Notepad', u'無題 - メモ帳'
    
    def active_notepad(self):
        try:
            win = guippy.Window()
            win.catch(*self.NOTEPAD)
            win.active()
        except Timeout:
            kbd = guippy.Keyboard()
            kbd.windows('r')
            kbd.enter('notepad')
            time.sleep(1)

class NormalizeTest(GuippyTest):
    def test_normalize_denormalize(self):
        from guippy.shortcut import Normalizer, Denormalizer
        
        def _func(normalize, denormalize, num):
            normal = normalize(num)
            ans = denormalize(normal)
            self.assert_(area(ans, num, 1),
                         '{0} -> {1} -> {2}'.format(num, normal, ans))
            
        for ii in range(LOOP_MAX):
            _func(Normalizer.xx, Denormalizer.xx, ii)
            _func(Normalizer.yy, Denormalizer.yy, ii)

class WindowTest(GuippyTest):
    def setUp(self):
        self.win = guippy.Window()

    def test_get_window(self):
        self.active_notepad()
        hwnd_aa = self.win.get_window()
        guippy.Keyboard.windows('d')
        hwnd_bb = self.win.get_window(*self.NOTEPAD)
        self.assertEqual(hwnd_aa, hwnd_bb)

    def test_catch(self):
        self.active_notepad()
        self.win.catch()
        hwnd_aa = self.win.hwnd
        guippy.Keyboard.windows('d')
        self.win.catch(*self.NOTEPAD)
        hwnd_bb = self.win.hwnd
        self.assertEqual(hwnd_aa, hwnd_bb)

    def _test_active(self):
        self.active_notepad()
        self.win.active()
        self.win.catch()
        hwnd_aa = self.win.hwnd
        guippy.Keyboard.windows('d')
        
        hwnd_bb = self.win.get_window()
        self.assertEqual(hwnd_aa, hwnd_bb)

    def test_rect(self):
        self.win.get_rect(True)
        self.win.get_rect(False)
    
    def test_get_popup(self):
        self.win.get_popup()

    def test_get_child(self):
        self.win.get_child()

class KeyboardTest(GuippyTest):
    def _test_punch(self):
        guippy.Keyboard.punch('#' + string.printable)

class KeycodeTest(GuippyTest):
    def test_char2codes(self):
        gen = guippy.keyboard.Keycode.char2codes('C')
        self.assertEqual((160, True, False), gen.next()) # push shift
        self.assertEqual((67, True, True), gen.next())   # push and release 'C'
        self.assertEqual((160, False, True), gen.next()) # release shift

        gen = guippy.keyboard.Keycode.char2codes('c')
        self.assertEqual((67, True, True), gen.next())   # push and release 'C'
        try:
            codes = gen.next()
        except StopIteration:
            pass # OK
        else:
            self.fail(codes)
    
    def test_func2codes(self):
        gen = guippy.keyboard.Keycode.func2codes(1)
        self.assertEqual((112, True, True), gen.next())
        
class ClipboardTest(GuippyTest):
    def test_test(self):
        data = ASCII_CHARS
        guippy.Clipboard.set(data)
        self.assertEqual(data, guippy.Clipboard.get())

class MouseTest(GuippyTest):
    def test_now(self):
        ms = guippy.Mouse()
        for ii in range(LOOP_MAX):
            self.assertEqual(ms.now(), ms.now())
            self.assertEqual(ms.now(True), ms.now(True))
            self.assertEqual(ms.now(False), ms.now(False))
            
    def _jumping_test(self, ms, normalize, absolute,
                      jump_coord, prediction_coord, now_coord, width):
        fmt = 'now={0}, prediction={1}'
        for ii in range(LOOP_MAX):
            xx, yy = jump_coord()
            ans_xx, ans_yy = prediction_coord(xx, yy)
            ms.jump(xx, yy, normalize, absolute)
            now_xx, now_yy = now_coord(xx, yy)
            self.assert_(area(now_xx, ans_xx, width),
                             fmt.format(now_xx, ans_xx))
            self.assert_(area(now_yy, ans_yy, width),
                             fmt.format(now_yy, ans_yy))
        
    def test_jump_normalize_absolute(self):
        ms = guippy.Mouse()
        normalize = True
        absolute = True
        
        def jump_coord():
            return random.randint(0, 0xFFFF), random.randint(0, 0xFFFF)

        def prediction_coord(xx, yy):
            return xx, yy
        
        def now_coord(xx, yy):
            return ms.now()
        
        width = 100
        self._jumping_test(ms, normalize, absolute,
                           jump_coord, prediction_coord, now_coord, width)
        
    def _test_jump_unnormalize_unabsolute(self):
        from guippy.shortcut import Display
        ms = guippy.Mouse()
        normalize = False
        absolute = False

        def jump_coord():
            _ = lambda n: random.randint(-n, n)
            return _(Display.XMAX), _(Display.YMAX)
        
        def prediction_coord(xx, yy):
            now_xx, now_yy = ms.now(normalize)
            return now_xx + xx, now_yy + yy
        
        def now_coord(*args, **kwds):
            return ms.now(normalize)
        width = 10
        self._jumping_test(ms, normalize, absolute,
                           jump_coord, prediction_coord, now_coord, width)
        

    def test_point(self):
        mouse = guippy.Mouse()
        mouse.jump(23, 45)
        mouse.point(34,63)

if __name__ == '__main__':
    unittest.main()
