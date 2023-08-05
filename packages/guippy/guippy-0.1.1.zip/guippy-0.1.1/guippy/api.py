#-*- coding: utf-8 -*-
"""I/F for Windows API.

I/F for to call Windows API, and those related to it.
"""
import util
import ctypes
from ctypes import WINFUNCTYPE
from ctypes.wintypes import BOOL, UINT, LONG, LPCWSTR, HWND, WPARAM, LPARAM, \
    RECT, HGLOBAL, LPVOID, HANDLE

LPCTSTR = LPCWSTR
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def errcheck_null(result, func, args):
    """Function of checking resutl value for WindowsAPI"""
    if result is None:
        raise ctypes.WinError()
    return args

def errcheck_nonull(result, func, args):
    if result is not None:
        raise ctypes.WinError()
    return args


def fptr_from_dll(dll, funcname, restype=None, errcheck=None):
    fptr = getattr(dll, funcname)
    if restype is not None:
        fptr.restype = restype
    if errcheck is not None:
        fptr.errcheck = errcheck
    return fptr

get_user32_api = lambda *args, **kwds: fptr_from_dll(user32, *args, **kwds)
get_kernel32_api = lambda *args, **kwds: fptr_from_dll(kernel32, *args, **kwds)

## ~~~ stdlib ~~~
strcpy = ctypes.cdll.msvcrt.strcpy
wcscpy = ctypes.cdll.msvcrt.wcscpy

## ~~~ WindowsAPI ~~~
_en = errcheck_null

FindWindow = WINFUNCTYPE(HWND, HWND, LPCTSTR)(
    ('FindWindowW', user32),
    ((1, 'lpClassName'), (1, 'lpWindowName'))
    )
FindWindow.errcheck = _en

FindWindowEx = WINFUNCTYPE(HWND, HWND, HWND, LPCTSTR, LPCTSTR)(
    ('FindWindowExW', user32),
    ((1, 'hwndParent'),
     (1, 'hwndChildAfter'),
     (1, 'lpClassName'),
     (1, 'lpWindowName'),
     ))
FindWindowEx.errcheck = _en

GetWindow = user32.GetWindow
GetForegroundWindow = user32.GetForegroundWindow
SetForegroundWindow = user32.SetForegroundWindow
GetWindowRect = user32.GetWindowRect
OpenIcon = user32.OpenIcon
CloseWindow = user32.CloseWindow
DestroyWindow = user32.DestroyWindow
ShowWindow = user32.ShowWindow
MoveWindow = user32.MoveWindow
#SendMessage = user32.SendMessage

GlobalAlloc = get_kernel32_api('GlobalAlloc', HGLOBAL, _en)
GlobalFree = get_kernel32_api('GlobalFree', HGLOBAL, errcheck_nonull)
GlobalLock = get_kernel32_api('GlobalLock', LPVOID, _en)
GlobalUnlock = get_kernel32_api('GlobalUnlock', BOOL, _en)
OpenClipboard = get_user32_api('OpenClipboard', BOOL, _en)
CloseClipboard = get_user32_api('CloseClipboard', BOOL, _en)
GetClipboardData = get_user32_api('GetClipboardData', HANDLE, _en)
SetClipboardData = get_user32_api('SetClipboardData', HANDLE, _en)
EmptyClipboard = get_user32_api('EmptyClipboard', BOOL, _en)

keybd_event = user32.keybd_event
mouse_event = user32.mouse_event

GetCursorPos = user32.GetCursorPos
GetSystemMetrics = user32.GetSystemMetrics
del _en
## ~~~ Windows Defines ~~~

SW_SHOWMAXIMIZED = 3
GMEM_DDESHARE = 0x2000

# defined in winbase.h
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
GHND = GMEM_MOVEABLE | GMEM_ZEROINIT

# defined in winuser.h
CF_TEXT = 1
CF_UNICODETEXT = 13

_sm = util.enum() # defined windows.h
SM_CXSCREEN = _sm()
SM_CYSCREEN = _sm()
del _sm

_gw = util.enum() # defined windows.h
GW_CHILD = _gw(5)
GW_ENABLEDPOPUP = _gw()
del _gw

_wm = util.enum()
WM_NULL = _wm(0x0000)
WM_DESTROY = _wm(0x0002)
WM_CLOSE = _wm(0x0010)
del _wm

_me = util.enum(0x0001, lambda x: x<<1) 
ME_MOVE = _me()
ME_LEFTDOWN = _me()
ME_LEFTUP = _me()
ME_RIGHTDOWN = _me()
ME_RIGHTUP = _me()
ME_MIDDLEDOWN = _me()
ME_MIDDLEUP = _me()
ME_WHEEL = _me(0x0800)
ME_ABSOLUTE = _me(0x8000)
del _me

_vk = util.enum()
VK_LBUTTON = _vk(0x01) # mouse left
VK_RBUTTON = _vk() # mouse right
VK_CANCEL = _vk()
VK_MBUTTON = _vk() # mouse middle
VK_XBUTTON1 = _vk()
VK_XBUTTON2 = _vk()
VK_RESV_7 = _vk()
VK_BACK = _vk() # back space
VK_TAB = _vk() # \t
VK_RESV_10 = _vk()
VK_RESV_11 = _vk()
VK_CLEAR = _vk()
VK_RETURN = _vk() # \n
VK_RESV_14 = _vk()
VK_RESV_15 = _vk()
VK_SHIFT = _vk() # shift
VK_CONTROL = _vk() # ctrl
VK_MENU = _vk() # alt (GRAPH)
VK_PAUSE = _vk() # pause
VK_CAPITAL = _vk() # caps lock
VK_KANA = HANGUL = _vk() # kana
VK_RESV_22 = _vk()
VK_JUNJA = _vk()
VK_FINAL = _vk()
VK_HANJA = KANJI = _vk() # kanji
VK_RESV_26 = _vk()
VK_ESCAPE = _vk() # escape
VK_CONVERT = _vk() # henkan
VK_NONCONVERT = _vk() # muhenkan
VK_ACCEPT = _vk()
VK_MODECHANGE = _vk()
VK_SPACE = _vk() # space
VK_PRIOR = _vk() # page up
VK_NEXT = _vk() # page down
VK_END = _vk() # end
VK_HOME = _vk() # home
VK_LEFT = _vk() # arrow
VK_UP = _vk() # arrow
VK_RIGHT = _vk() # arrow
VK_DOWN = _vk() # arrow
VK_SELECT = _vk()
VK_PRINT = _vk()
VK_EXECUTE = _vk()
VK_SNAPSHOT = _vk() # print screen
VK_INSERT = _vk() # insert
VK_DELETE = _vk() # delete
VK_HELP = _vk()
VK_N0 = _vk() # 0
VK_N1 = _vk() # 1
VK_N2 = _vk() # 2
VK_N3 = _vk() # 3
VK_N4 = _vk() # 4
VK_N5 = _vk() # 5
VK_N6 = _vk() # 6
VK_N7 = _vk() # 7
VK_N8 = _vk() # 8
VK_N9 = _vk() # 9
# reserve
VK_A = _vk(0x41) # alphabet
VK_B = _vk() # alphabet
VK_C = _vk() # alphabet
VK_D = _vk() # alphabet
VK_E = _vk() # alphabet
VK_F = _vk() # alphabet
VK_G = _vk() # alphabet
VK_H = _vk() # alphabet
VK_I = _vk() # alphabet
VK_J = _vk() # alphabet
VK_K = _vk() # alphabet
VK_L = _vk() # alphabet
VK_M = _vk() # alphabet
VK_N = _vk() # alphabet
VK_O = _vk() # alphabet
VK_P = _vk() # alphabet
VK_Q = _vk() # alphabet
VK_R = _vk() # alphabet
VK_S = _vk() # alphabet
VK_T = _vk() # alphabet
VK_U = _vk() # alphabet
VK_V = _vk() # alphabet
VK_W = _vk() # alphabet
VK_X = _vk() # alphabet
VK_Y = _vk() # alphabet
VK_Z = _vk() # alphabet
VK_LWIN = _vk() # windows key left
VK_RWIN = _vk() # windows key right
VK_APPS = _vk() # application key
VK_RESV_94 = _vk()
VK_SLEEP = _vk()
VK_NUMPAD0 = _vk() # Num 0
VK_NUMPAD1 = _vk() # Num 1
VK_NUMPAD2 = _vk() # Num 2
VK_NUMPAD3 = _vk() # Num 3
VK_NUMPAD4 = _vk() # Num 4
VK_NUMPAD5 = _vk() # Num 5
VK_NUMPAD6 = _vk() # Num 6
VK_NUMPAD7 = _vk() # Num 7
VK_NUMPAD8 = _vk() # Num 8
VK_NUMPAD9 = _vk() # Num 9
VK_MULTIPLY = _vk() # Num *
VK_ADD = _vk() # Num +
VK_SEPARATOR = _vk() # Num ,
VK_SUBTRACT = _vk() # Num -
VK_DECIMAL = _vk() # Num .
VK_DIVIDE = _vk() # Num /
VK_F1 = _vk() # function key
VK_F2 = _vk() # function key
VK_F3 = _vk() # function key
VK_F4 = _vk() # function key
VK_F5 = _vk() # function key
VK_F6 = _vk() # function key
VK_F7 = _vk() # function key
VK_F8 = _vk() # function key
VK_F9 = _vk() # function key
VK_F10 = _vk() # function key
VK_F11 = _vk() # function key
VK_F12 = _vk() # function key
VK_F13 = _vk() # function key
VK_F14 = _vk() # function key
VK_F15 = _vk() # function key
VK_F16 = _vk() # function key
VK_F17 = _vk() # function key
VK_F18 = _vk() # function key
VK_F19 = _vk() # function key
VK_F20 = _vk() # function key
VK_F21 = _vk() # function key
VK_F22 = _vk() # function key
VK_F23 = _vk() # function key
VK_F24 = _vk() # function key
# reserve
VK_NUMLOCK = _vk(0X90) # NumLock
VK_SCROLL = _vk() # ScrollLock
VK_EQUAL = _vk() # Num =
# RESERV
VK_LSHIFT = _vk(0xa0) # shift left
VK_RSHIFT = _vk() # shift right
VK_LCONTROL = _vk() # ctrl left
VK_RCONTROL = _vk() # ctrl right
VK_LMENU = ALT_L = _vk() # alt left
VK_RMENU = ALT_R = _vk() # alt right
VK_BROWSER_BACK = _vk()
VK_BROWSER_FORWARD = _vk()
VK_BROWSER_REFRESH = _vk()
VK_BROWSER_STOP = _vk()
VK_BROWSER_SEARCH = _vk()
VK_BROWSER_FAVORITES = _vk()
VK_BROWSER_HOME = _vk()
VK_VOLUME_MUTE = _vk()
VK_VOLUME_DOWN = _vk()
VK_VOLUME_UP = _vk()
VK_MEDIA_NEXT_TRACK = _vk()
VK_MEDIA_PREV_TRACK = _vk()
VK_MEDIA_STOP = _vk()
VK_MEDIA_PLAY_PAUSE = _vk()
VK_LAUNCH_MAIL = _vk()
VK_LAUNCH_MEDIA_SELECT = _vk()
VK_LAUNCH_APP1 = _vk()
VK_LAUNCH_APP2 = _vk()
VK_RESV_184 = _vk()
VK_RESV_185 = _vk()
VK_OEM_1 = COLON = VK_COLON = _vk() # :
VK_OEM_PLUS = SEMICOLON = VK_SEMICOLON = _vk() # ;
VK_OEM_COMMA = COMMA = VK_COMMA = _vk() # ,
VK_OEM_MINUS = MINUS = VK_MINUS = _vk() # -
VK_OEM_PERIOD = DOT = VK_DOT = _vk() # .
VK_OEM_2 = SLASH = VK_SLASH = _vk() # /
VK_OEM_3 = AT = VK_AT =  _vk() # @
# reserve
VK_OEM_4 = BOX_O = VK_BOX_O = _vk(0xdb) # [
VK_OEM_5 = BACKSLASH = VK_BACKSLASH = _vk() # \
VK_OEM_6 = BOX_C = VK_BOX_C = _vk() # ]
VK_OEM_7 = CARET = VK_CARET = _vk() # ^
VK_OEM_8 =  _vk() # _
VK_RESV_224 = _vk()
VK_OEM_AX = _vk()
VK_OEM_102 = UNDERLINE = VK_UNDERLINE = _vk() # _
VK_ICO_HELP = _vk()
VK_ICO_00 = _vk()
VK_PROCESSKEY = _vk()
VK_PACKET = _vk()
VK_RESV_232 = _vk()
VK_OEM_RESET = _vk()
VK_OEM_JUMP = _vk()
VK_OEM_PA1 = _vk()
VK_OEM_PA2 = _vk()
VK_OEM_PA3 = _vk()
VK_OEM_WSCTRL = _vk()
VK_OEM_CUSEL = _vk()
VK_OEM_ATTN = _vk()
VK_OEM_FINISH = _vk()
VK_OEM_COPY = _vk()
VK_OEM_AUTO = _vk()
VK_OEM_ENLW = _vk()
VK_OEM_BACKTAB = _vk()
VK_ATTN = _vk()
VK_CRSEL = _vk()
VK_EXSEL= _vk()
VK_EREOF = _vk()
VK_PLAY = _vk()
VK_ZOOM = _vk()
VK_NONAME = _vk()
VK_PA1 = _vk()
VK_OEM_CLEAR = _vk()
del _vk

KEYUP = 2

class SystemMetrics(object):
    """System metrics class

    This class is utility. Can use statically.
    """
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1

    @staticmethod
    def get(screen):
        """Getting the system metrics.
        
        The screen is constant for the system metrics. Must be either SM_CXSCREEN
        or SM_CYSCREEN. However, even if you give the other value, it will not
        error. It will return GetSystemMetrics() of Windows API returned value.
        """
        return user32.GetSystemMetrics(screen)
    
    @classmethod
    def X(cls):
        """Getting X of system metcics."""
        return cls.get(cls.SM_CXSCREEN)
        
    @classmethod
    def Y(cls):
        """Getting Y of system metrics."""
        return cls.get(cls.SM_CYSCREEN)
        


        
