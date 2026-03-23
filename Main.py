# coding:utf-8
"""
WordCloud-Gui 增强版
词云生成GUI工具
"""
import wx
import os
import sys

# 支持Python 3.x
if sys.version_info[0] >= 3:
    unicode = str

from MyUI.MainFrame import LabelBookDemo
from Utils import gl

class MyApp(wx.App):
    def OnInit(self):
        try:
            gl.CWD = os.getcwd()
            print(f"当前工作目录: {gl.CWD}")
        except Exception as e:
            print(f"获取工作目录失败: {e}")
            gl.CWD = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        self.win = LabelBookDemo(parent=None)
        self.SetTopWindow(self.win)
        self.win.SetTitle(u"WordCloud-Gui 增强版 - 词云生成工具")
        self.win.Show(True)
        return True
    
    def OnExit(self):
        """程序退出时清理临时文件"""
        catch_folder = os.path.join(gl.CWD, "data", ".catch")
        if os.path.exists(catch_folder):
            try:
                import shutil
                shutil.rmtree(catch_folder)
                os.makedirs(catch_folder, exist_ok=True)
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        else:
            os.makedirs(catch_folder, exist_ok=True)
        return 0


if __name__ == "__main__":
    app = MyApp(redirect=False)
    app.MainLoop()
