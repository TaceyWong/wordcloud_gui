# coding:utf-8

import wx
import wx.richtext

__author__ = 'Tacey Wong'
__date__   = "2016年元月"

###########################################################################
##关于
###########################################################################

class MyAbout(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_richText1 = wx.richtext.RichTextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                                   wx.TE_READONLY| wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.WANTS_CHARS)
        bSizer1.Add(self.m_richText1, 1, wx.EXPAND | wx.ALL, 5)

        self.m_hyperlink1 = wx.HyperlinkCtrl(self, wx.ID_ANY, u"Tacey 词云源码网址", u"http://www.github.com/iTacey/wordcloud_gui",
                                             wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE)
        bSizer1.Add(self.m_hyperlink1, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

    def __del__(self):
        pass

    def update_Choice(self):
        pass


