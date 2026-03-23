# coding:utf-8

import wx
import os
import sys

from MyUI.MainFrame import LabelBookDemo
from Utils import gl


class MyApp(wx.App):
    
    def OnInit(self):
        try:
            gl.CWD = gl.get_base_dir()
            print(f"工作目录: {gl.CWD}")
        except Exception as e:
            print(f"获取工作目录失败: {e}")
        
        gl.ensure_catch_dir()
        
        self.win = LabelBookDemo(parent=None)
        self.SetTopWindow(self.win)
        self.win.SetTitle(f"{gl.APP_NAME} v{gl.APP_VERSION}")
        self.win.Show(True)
        
        return True
    
    def OnExit(self):
        gl.cleanup_catch_dir()
        return 0


class MyFrame(wx.Frame):
    pass


def main():
    app = MyApp(redirect=False)
    app.MainLoop()


if __name__ == "__main__":
    main()
