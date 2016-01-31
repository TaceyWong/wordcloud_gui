# coding:utf-8

import wx
import wx.richtext
from  Utils import gl

__author__ = 'Tacey Wong'
__date__ = "2016年元月"

###########################################################################
##关于
###########################################################################

class MyAbout(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.m_richText1 = wx.richtext.RichTextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                                    wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.WANTS_CHARS)
        bSizer1.Add(self.m_richText1, 1, wx.EXPAND | wx.ALL, 5)

        self.m_hyperlink1 = wx.HyperlinkCtrl(self, wx.ID_ANY, u"Tacey 词云源码网址",
                                             u"http://www.github.com/iTacey/wordcloud_gui",
                                             wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE)
        bSizer1.Add(self.m_hyperlink1, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

    def __del__(self):
        pass

    def update_Choice(self):
        pass
        MIT_license = u"""
#Tacey 词云——桌面词云生成软件
#作者：Tacey Wong(负责界面功能整合)

+  本软件除软件使用的字体外遵循MIT协议，免费共享

#协议简要
+  ①被授权人有权利使用、复制、修改、合并、出版发行、散布、再授权及贩售软体及软体的副本。
+  ②被授权人可根据程式的需要修改授权条款为适当的内容。
+  ③在软件和软件的所有副本中都必须包含版权声明和许可声明。

#协议全文

#The MIT License (MIT)
#Copyright © 2016 Tacey Wong, https://github.com/iTacey
+  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

+  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

+  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
        MIT_license = MIT_license.split("\n")
        self.m_richText1.Clear()
        for i in MIT_license:
            if i.startswith("#"):
                self.m_richText1.BeginAlignment(wx.TEXT_ALIGNMENT_CENTRE)
                self.m_richText1.WriteText(i[1:])
                self.m_richText1.Newline()
                self.m_richText1.EndAlignment()

            if i.startswith("+"):
                self.m_richText1.WriteText(i[1:])
                self.m_richText1.Newline()
                # try:
                # with open(gl.CWD+"\\Doc\\about.txt") as f:
                #         for i in f.readlines():
                #             print i
                #             if i.startswith("#"):
                #                 self.m_richText1.BeginAlignment(wx.TEXT_ALIGNMENT_CENTRE)
                #                 self.m_richText1.WriteText(i[1:])
                #                 self.m_richText1.Newline()
                #                 self.m_richText1.EndAlignment()
                #
                #             if i.startswith("+"):
                #                 self.m_richText1.WriteText(i[1:])
                #                 self.m_richText1.Newline()
                # except Exception,e:
                #     print e


