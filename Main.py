# coding:utf-8

import wx
import os

from MyUI.MainFrame import *
from Utils import DB, gl,check
#
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class MyApp(wx.App):
    def OnInit(self):
        
        try:
            gl.CWD = os.getcwd()
            print gl.CWD
        except:
            pass

        self.win = LabelBookDemo(parent=None)
        self.SetTopWindow(self.win)
        self.win.SetTitle(u"Tacey 词云" )
        self.win.Show(True)
        return True

    def OnExit(self):
        try:
            pass
        except:
            pass


class MyFrame(wx.Frame):
    pass


if __name__ == "__main__":
    app = MyApp(redirect=False)
    app.MainLoop()