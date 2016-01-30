# coding:utf-8

__author__ = 'Tacey Wong'
__date__   = "2016年元月"

import wx
import wx.lib.colourselect as csel
import random

import os
import sys
import time
import datetime
from Utils import gl

from MyUI import *
from MyNormal import *
from MyText import *
from MyWeb import *
from MyHelp import *
from MyAbout import *

# try:
# dirName = os.path.dirname(os.path.abspath(__file__))
# except:
#     dirName = os.path.dirname(os.path.abspath(sys.argv[0]))




try:
    from agw import labelbook as LB
    from agw.fmresources import *
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.labelbook as LB
    from wx.lib.agw.fmresources import *

import images

_pageTexts = [u"格式文件词云生成", u"文本词云生成", u"网页文件词云生成", u"使用帮助", u"关于本软件"]

_pageIcons = ["text.png", "book.png", "web.png", "help.png", "about.png"]

_pages = [MyNormal, MyText, MyWeb, MyHelp, MyAbout]








class LabelBookDemo(wx.Frame):
    def __init__(self, parent):

        wx.Frame.__init__(self, parent)

        self.initializing = True
        self.book = None
        self._oldTextSize = 1.0

        # self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D |
        #                                                   wx.SP_LIVE_UPDATE | wx.SP_3DSASH | wx.SP_BORDER)  #wx.SP_BORDER
        # self.mainpanel = wx.Panel(self.splitter, -1)
        # self.toppanel = wx.Panel(self.splitter, -1, style=0)

        self.SetProperties()
        self.CreateLabelBook()
        self.DoLayout()

        # 窗口底部状态栏
        statusbar = self.CreateStatusBar(3, wx.ST_SIZEGRIP)
        statusbar.SetStatusWidths([-2, -1,-1])
        statusbar_fields = [(u"Tacey 词云,桌面单词云生成GUI软件。By Tacey Wong @ 2016"),
                            (u"MIT协议下免费分享，欢迎您的使用!")]
        for i in range(len(statusbar_fields)):
            statusbar.SetStatusText(statusbar_fields[i], i)
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()

        self.CenterOnScreen()  #设置窗口显示位置为屏幕中央
        self.initializing = False
        self.SendSizeEvent()
        self.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self,event):
        pass
        print event.GetSelection()
        self.book.GetCurrentPage().update_Choice()
        print event.GetSelection()
        # if event.GetSelection() == 0:
        #     self.book.GetCurrentPage().test()
        # num = event.GetSelection()
        # if num == 2:
        #     self.book.GetCurrentPage().update_corpus_Choice()
        # if num == 3:
        #     self.book.GetCurrentPage().updatecorpus()


    def SetProperties(self):

        # self.SetTitle(u"涉华英语自动提取及检索平台_%s_%s"%(gl.USER_NAME,gl.USER_POWER))
        self.icon = wx.Icon("img/logo.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        c_x, c_y, c_w, c_h = wx.ClientDisplayRect()
        print c_w, c_h, c_x, c_y
        self.SetSize((900, 600))
        # self.splitter.SetMinimumPaneSize(0)


    def DoLayout(self):


        self.panelsizer = wx.BoxSizer(wx.VERTICAL)
       

        self.panelsizer.Add(self.book, 1, wx.EXPAND, 0)
        self.SetSizer(self.panelsizer)
        self.panelsizer.Layout()

        self.panelsizer.Layout()
        self.Layout()


    def CreateLabelBook(self, btype=0):

        if not self.initializing:
            self.Freeze()
            self.panelsizer = self.GetSizer()
            self.panelsizer.Detach(0)
            self.book.Destroy()
        else:
            self.imagelist = self.CreateImageList()

        style = self.GetBookStyles()

        # 是一个labelbook，不是FlatImageBook
        self.book = LB.LabelBook(self, -1, agwStyle=style)

        self.SetUserColours()
        self.book.SetFontSizeMultiple(1.0)
        self.book.SetFontBold(False)

        self.book.AssignImageList(self.imagelist)

        for indx, Class in enumerate(_pages):
            self.book.AddPage(Class(self.book),
                              _pageTexts[indx], True, indx)

        # self.book.AddPage(MyHome(self.book, _pageColours[0],"This is panel number 0" ),
        #                   _pageTexts[0], True, 0)
        # self.book.AddPage(MyProcess(self.book, _pageColours[1],"This is panel number 1" ),
        #                   _pageTexts[1], True, 1)
        # self.book.AddPage(MySearch(self.book, _pageColours[2],"This is panel number 2" ),
        #                   _pageTexts[2], True, 2)
        # self.book.AddPage(MyLogin(cursor=self.cursor),
        #                   _pageTexts[3], True, 3)

        self.book.SetSelection(0)



        if not self.initializing:
            self.panelsizer.Add(self.book, 1, wx.EXPAND)
            self.panelsizer.Layout()
            self.GetSizer().Layout()
            self.Layout()
            self.Thaw()

        self.SendSizeEvent()


    def GetBookStyles(self):

        style = INB_FIT_BUTTON
        style |= INB_LEFT  # INB_RIGHT # INB_TOP # INB_BOTTOM
        style |= INB_SHOW_ONLY_TEXT
        style |= INB_SHOW_ONLY_IMAGES
        style |= INB_USE_PIN_BUTTON
        style |= INB_DRAW_SHADOW
        # style |= INB_WEB_HILITE
        # style |= INB_GRADIENT_BACKGROUND
        style |= INB_BORDER
        style |= INB_FIT_LABELTEXT
        style |= INB_BOLD_TAB_SELECTION

        if self.book:
            self.book.SetFontBold(1.0)

        return style


    def CreateImageList(self):

        imagelist = wx.ImageList(32, 32)
        for img in _pageIcons:
            newImg = gl.BITMAP_DIR + "lb%s" % img
            bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
            imagelist.Add(bmp)

        return imagelist


    def OnBookType(self, event):

        self.CreateLabelBook(event.GetInt())
        event.Skip()





        # self.book.Refresh()


    def SetUserColours(self):

        self.book.SetColour(INB_TAB_AREA_BACKGROUND_COLOUR, wx.Colour(132, 164, 213))
        self.book.SetColour(INB_ACTIVE_TAB_COLOUR, wx.Colour(255, 255, 255))
        self.book.SetColour(INB_TABS_BORDER_COLOUR, wx.Colour(0, 0, 204))
        self.book.SetColour(INB_TEXT_COLOUR, wx.BLACK)
        self.book.SetColour(INB_ACTIVE_TEXT_COLOUR, wx.BLACK)
        self.book.SetColour(INB_HILITE_TAB_COLOUR, wx.Colour(191, 216, 216))

    def Notify(self):
        # t = time.localtime(time.time())
        # st = time.strftime("%d-%b-%Y   %I:%M:%S", t)

        gl.TIME_NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.SetStatusText(u"当前时间为" + gl.TIME_NOW, 2)
        # self.log.WriteText("tick...\n")


if __name__ == '__main__':
    app = wx.App(False)
    win = LabelBookDemo(parent=None)
    win.Show(True)
    app.MainLoop()

