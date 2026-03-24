# coding:utf-8
"""
WordCloud GUI - 词云生成工具主程序
支持跨平台运行 (Windows/macOS/Linux)
"""

from __future__ import print_function, unicode_literals
import wx
import os
import sys

# 添加项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from MyUI.MainFrame import *
from Utils import gl

# Python 2/3 兼容性处理
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding("utf-8")


class MyApp(wx.App):
    """应用程序类"""

    def OnInit(self):
        try:
            gl.CWD = BASE_DIR
            print("Working directory:", gl.CWD)
        except Exception as e:
            print("Error setting working directory:", e)

        # 创建主窗口
        self.win = LabelBookDemo(parent=None)
        self.SetTopWindow(self.win)
        self.win.SetTitle(u"WordCloud GUI - 智能词云生成工具 v2.0")
        self.win.Show(True)

        return True

    def OnExit(self):
        """程序退出时清理临时文件"""
        try:
            catch_folder = os.path.join(gl.CWD, "data", ".catch")
            if os.path.exists(catch_folder):
                try:
                    import shutil
                    shutil.rmtree(catch_folder)
                    os.makedirs(catch_folder)
                except Exception as e:
                    print("Cleanup error:", e)
            else:
                os.makedirs(catch_folder)
        except Exception as e:
            print("OnExit error:", e)


if __name__ == "__main__":
    # 启用高DPI支持
    if hasattr(wx, 'EnableHighDPI'):
        wx.EnableHighDPI()

    app = MyApp(redirect=False)
    app.MainLoop()
