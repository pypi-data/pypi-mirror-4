#-*- coding: utf-8 -*-

class Application(object):
    @classmethod
    def names(cls):
        return cls.CNAME, cls.WNAME
    
class Notepad(Application):
    CNAME = 'Notepad'
    WNAME = u'無題 - メモ帳'
