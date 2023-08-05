#-*- coding: utf-8 -*-
"""To emulate keyboard.

"""
import api
from .api import keybd_event, KEYUP
from .decorator import interval

import time

PUSH_DEFAULT = True
RELEASE_DEFAULT = True

def special_key(func):
    def _wrap(obj, message='', push=True, release=True):
        code = func(obj)
        if push:
            obj.push(code)
        obj.punch(message)
        if release:
            obj.release(code)
    return _wrap

class KeyboardCore(object):
    @classmethod
    @interval
    def push(cls, code):
        """Push the key.
        """
        return keybd_event(code, 0, 0, 0)
        
    @classmethod
    @interval
    def release(cls, code):
        """Release the key.
        """
        return keybd_event(code, 0, KEYUP, 0)
    
    @classmethod
    def key(cls, code, push=PUSH_DEFAULT, release=RELEASE_DEFAULT):
        if push:
            cls.push(code)

        if release:
            cls.release(code)

    @classmethod
    def _put(cls, char):
        """Input a character.
        """
        for code, push, release in Keycode.char2codes(char):
            cls.key(code, push, release)

    @classmethod
    def punch(cls, message):
        """Input messages.
        """
        for char in message:
            cls._put(char)

class KeyboardElement(KeyboardCore):
    @classmethod
    def F(cls, num):
        """Type the function key.
         Avariable num is integer. It is processing after convert integer.
        If can not convert integer then will raise TypeError.
        """
        for code, push, release in Keycode.func2codes(num):
            cls.key(code, push, release)

    @classmethod
    @special_key
    def ctrl(cls):
        """Type the control key."""
        return api.VK_LCONTROL

    @classmethod
    @special_key
    def alt(cls):
        """Type the alt key."""
        return api.VK_ALT_L

    @classmethod
    @special_key
    def fn(cls):
        """Type the fn key."""
        assert False, 'not support'
    
    @classmethod
    @special_key
    def shift(cls):
        """Type the shift key."""
        return api.VK_SHIFT

    @classmethod
    @special_key
    def capslock(cls):
        """Type the caps lock key."""
        return api.VK_CAPITAL

    @classmethod
    @special_key
    def tab(cls):
        """Type the tab key."""
        return api.VK_TAB

    @classmethod
    @special_key
    def lang(cls):
        """Tpe a language key.
         Use to switch between input languages. Change language is depends on a
        respectively system.
        """
        return api.VK_OEM_AUTO

    @classmethod
    def space(cls):
        cls.punch(' ')

    @classmethod
    @special_key
    def _windows(cls):
        return api.VK_LWIN

    @classmethod
    def windows(cls, *args, **kwds):
        cls._windows(*args, **kwds)
        time.sleep(1)
        

    @classmethod
    @special_key
    def mac(cls):
        assert False, 'not supported'

    @classmethod
    @special_key
    def up(cls):
        return api.VK_UP

    @classmethod
    @special_key
    def down(cls):
        return api.VK_DOWN

    @classmethod
    @special_key
    def right(cls):
        return api.VK_RIGHT

    @classmethod
    @special_key
    def left(cls):
        return api.VK_LEFT

    @classmethod
    def enter(cls, message=''):
        cls.punch(message+'\n')

    @classmethod
    @special_key
    def backspace(cls):
        return api.VK_BACK
    
    @classmethod
    @special_key
    def insert(cls):
        return api.INSERT
    
    @classmethod
    @special_key
    def delete(cls):
        return api.VK_DELETE

    @classmethod
    @special_key
    def menu(cls):
        return api.VK_MENU

    @classmethod
    @special_key
    def printscreen(cls):
        return api.VK_SNAPSHOT

    @classmethod
    @special_key
    def numlock(cls):
        return api.VK_NUMLOCK

    @classmethod
    @special_key
    def pause(cls):
        return api.VK_PAUSE

    @classmethod
    @special_key
    def home(cls):
        return api.VK_HOME

    @classmethod
    @special_key
    def end(cls):
        return api.VK_END

    @classmethod
    @special_key
    def page_up(cls):
        return api.VK_PRIOR

    @classmethod
    @special_key
    def page_down(cls):
        return api.VK_NEXT

    @classmethod
    @special_key
    def escape(cls):
        return api.VK_ESCAPE

    @classmethod
    @special_key
    def convert(cls):
        return api.VK_CONVERT

    @classmethod
    @special_key
    def nonconvert(cls):
        return api.VK_NONCONVERT

    @classmethod
    @special_key
    def kana(cls):
        return VK_KANA

class Keyboard(KeyboardElement):
    def comb(self):
        pass

class Keycode(object):
    FUNC_CODE = {1: api.VK_F1,
                 2: api.VK_F2,
                 3: api.VK_F3,
                 4: api.VK_F4,
                 5: api.VK_F5,
                 6: api.VK_F6,
                 7: api.VK_F7,
                 8: api.VK_F8,
                 9: api.VK_F9,
                 10: api.VK_F10,
                 11: api.VK_F11,
                 12: api.VK_F12,
                 13: api.VK_F13,
                 14: api.VK_F14,
                 15: api.VK_F15,
                 16: api.VK_F16,
                 17: api.VK_F17,
                 18: api.VK_F18,
                 19: api.VK_F19,
                 20: api.VK_F20,
                 21: api.VK_F21,
                 22: api.VK_F22,
                 23: api.VK_F23,
                 24: api.VK_F24,
                 }

    CHAR_CODE = {'\t': api.VK_TAB,
                 '\n': api.VK_RETURN,
                 ' ': api.VK_SPACE,
                 '-': api.VK_MINUS,
                 '^': api.VK_CARET,
                 '\\': api.VK_BACKSLASH,
                 '@': api.VK_AT,
                 '[': api.VK_BOX_O,
                 ';': api.VK_SEMICOLON,
                 ':': api.VK_COLON,
                 ']': api.VK_BOX_C,
                 ',': api.VK_COMMA,
                 '.': api.VK_DOT,
                 '/': api.VK_SLASH,
                 api.VK_UNDERLINE: api.VK_UNDERLINE, # -
                 }

    SHIFT_CHAR = {'!': '1',
                  '"': '2',
                  '#': '3',
                  '$': '4',
                  '%': '5',
                  '&': '6',
                  "'": '7',
                  '(': '8',
                  ')': '9',
                  '=': '-',
                  '~': '^',
                  '|': '\\',
                  '`': '@',
                  '{': '[',
                  '+': ';',
                  '*': ':',
                  '}': ']',
                  '<': ',',
                  '>': '.',
                  '?': '/',
                  '_': api.VK_UNDERLINE,
                  }
    
    @classmethod
    def char2codes(cls, char):
        char = str(char)
        shift_on = False
        try:
            if char.isupper():
                pass
            elif char.islower():
                raise KeyError # unuse shift key
            else:# a mark
                char = cls.SHIFT_CHAR[char]
        except KeyError:
            pass
        else: # on shift procedure
            yield api.VK_LSHIFT, True, False
            shift_on = True
        
        code = None
        try:
            code = cls.CHAR_CODE[char]
        except KeyError:
            code = ord(char.upper())
        assert code, 'not support char: {0}'.format(char)
        yield code, True, True
        
        # shift procedure
        if shift_on:
            yield api.VK_LSHIFT, False, True

    @classmethod
    def func2codes(cls, num):
        try:
            code = cls.FUNC_CODE[num]
        except KeyError, err:
            assert False, 'Not support char: {0}'.format(num)
        else:
            yield code, True, True
