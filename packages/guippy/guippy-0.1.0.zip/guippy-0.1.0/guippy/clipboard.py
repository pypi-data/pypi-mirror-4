#-*- coding: utf-8 -*-
"""For clipboard.
"""
from .api import HWND, GlobalLock, OpenClipboard, GetClipboardData,\
    CF_UNICODETEXT, GlobalUnlock, CloseClipboard

import ctypes

class Clipboard(object):
    """Control clipboard."""

    @staticmethod
    def set(self, data):
        """Copy a data to clipboard."""
        pass

    @staticmethod
    def get(self, hwnd=None):
        """Get a clipboard data."""
        if hwnd is None:
            hwnd = HWND(0)
        
        org_restype = GlobalLock.restype

        OpenClipboard(hwnd)
        try:
            hmem = GetClipboardData(CF_UNICODETEXT)
            GlobalLock.restype = ctypes.c_wchar_p
            try: 
                return GlobalLock(ctypes.c_int(hmem)) # return unicode text
            finally:
                GlobalUnlock(hmem)
        finally:
            GlobalLock.restype = org_restype 
            CloseClipboard()
        
