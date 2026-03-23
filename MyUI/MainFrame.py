# coding:utf-8

__author__ = 'Tacey Wong'
__date__ = "2016年元月"

import wx
import wx.lib.colourselect as csel
import random

import os
import sys
import time
import datetime
from Utils import gl

from MyUI import images

try:
    from agw import labelbook as LB
    from agw.fmresources import *
except ImportError:
    import wx.lib.agw.labelbook as LB
    from wx.lib.agw.fmresources import *


_pageTexts = [
    "数据导入",
    "文本词云",
    "格式文件词云",
    "词频分析",
    "批量处理",
    "使用帮助",
    "关于软件"
]

_pageIcons = [
    "folder_new.png",
    "text.png",
    "book.png",
    "item.png",
    "filenew.png",
    "help.png",
    "about.png"
]


def _lazy_import_pages():
    from MyUI.MyDataImport import MyDataImport
    from MyUI.MyText import MyText
    from MyUI.MyNormal import MyNormal
    from MyUI.MyFrequency import MyFrequency
    from MyUI.MyBatch import MyBatch
    from MyUI.MyHelp import MyHelp
    from MyUI.MyAbout import MyAbout
    return [MyDataImport, MyText, MyNormal, MyFrequency, MyBatch, MyHelp, MyAbout]


_pages = None


class LabelBookDemo(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        
        self.initializing = True
        self.book = None
        self._oldTextSize = 1.0
        self.current_theme = gl.CURRENT_THEME
        
        self.SetProperties()
        self.CreateLabelBook()
        self.DoLayout()
        self.create_menubar()
        
        statusbar = self.CreateStatusBar(3, wx.STB_SIZEGRIP)
        statusbar.SetStatusWidths([-2, -1, -1])
        statusbar_fields = [
            f"{gl.APP_NAME} v{gl.APP_VERSION} - 词云生成桌面工具",
            f"作者: {gl.APP_AUTHOR}"
        ]
        for i in range(len(statusbar_fields)):
            statusbar.SetStatusText(statusbar_fields[i], i)
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(1000)
        self.Notify()
        
        self.CenterOnScreen()
        self.initializing = False
        self.SendSizeEvent()
        self.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def OnTimer(self, event):
        self.Notify()
    
    def OnClose(self, event):
        gl.cleanup_catch_dir()
        event.Skip()
    
    def create_menubar(self):
        menu_data = [
            ("文件(&F)", (
                ("新建项目(&N)", "新建词云项目", self.OnNew),
                ("打开文件(&O)", "打开数据文件", self.OnOpen),
                ("保存词云(&S)", "保存当前词云", self.OnSave),
                ("", "", ""),
                ("导出报告(&E)", "导出分析报告", self.OnExportReport),
                ("", "", ""),
                ("退出(&X)", "退出程序", self.OnExit)
            )),
            ("编辑(&E)", (
                ("清空缓存(&C)", "清空临时缓存文件", self.OnClearCache),
            )),
            ("视图(&V)", (
                ("亮色主题(&L)", "切换到亮色主题", self.OnLightTheme, wx.ITEM_RADIO),
                ("暗色主题(&D)", "切换到暗色主题", self.OnDarkTheme, wx.ITEM_RADIO),
            )),
            ("帮助(&H)", (
                ("使用帮助(&H)", "查看使用帮助", self.OnHelp),
                ("关于(&A)", "关于本软件", self.OnAbout),
            ))
        ]
        
        menuBar = wx.MenuBar()
        for eachMenuData in menu_data:
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.create_menu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
    
    def create_menu(self, menuData):
        menu = wx.Menu()
        for eachItem in menuData:
            if len(eachItem) == 2:
                label = eachItem[0]
                subMenu = self.create_menu(eachItem[1])
                menu.AppendMenu(wx.NewIdRef(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu
    
    def createMenuItem(self, menu, label, status, handler, kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(wx.ID_ANY, label, status, kind)
        self.Bind(wx.EVT_MENU, handler, menuItem)
    
    def OnNew(self, event):
        pass
    
    def OnOpen(self, event):
        pass
    
    def OnSave(self, event):
        pass
    
    def OnExportReport(self, event):
        pass
    
    def OnClearCache(self, event):
        gl.cleanup_catch_dir()
        dlg = wx.MessageDialog(self, '缓存已清空！', '操作完成',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnLightTheme(self, event):
        self.apply_theme('light')
    
    def OnDarkTheme(self, event):
        self.apply_theme('dark')
    
    def apply_theme(self, theme_name):
        if gl.set_theme(theme_name):
            self.current_theme = theme_name
            self.Refresh()
            self.Update()
            
            dlg = wx.MessageDialog(self, f'已切换到{gl.THEMES[theme_name]["name"]}，部分界面需要重启生效。',
                                   '主题切换', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
    
    def OnExit(self, event):
        self.Close()
    
    def OnHelp(self, event):
        self.book.SetSelection(5)
    
    def OnAbout(self, event):
        self.book.SetSelection(6)
    
    def OnPageChanged(self, event):
        current_page = self.book.GetCurrentPage()
        if hasattr(current_page, 'update_Choice'):
            current_page.update_Choice()
        if hasattr(current_page, 'refresh_data'):
            current_page.refresh_data()
        event.Skip()
    
    def SetProperties(self):
        icon_path = gl.get_path('img', 'logo.ico')
        if os.path.exists(icon_path):
            self.icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.icon)
        
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        c_x, c_y, c_w, c_h = wx.ClientDisplayRect()
        self.SetSize((1000, 700))
        self.SetMinSize((800, 600))
    
    def DoLayout(self):
        self.panelsizer = wx.BoxSizer(wx.VERTICAL)
        self.panelsizer.Add(self.book, 1, wx.EXPAND, 0)
        self.SetSizer(self.panelsizer)
        self.panelsizer.Layout()
        self.Layout()
    
    def CreateLabelBook(self):
        if not self.initializing:
            self.Freeze()
            self.panelsizer = self.GetSizer()
            self.panelsizer.Detach(0)
            self.book.Destroy()
        else:
            self.imagelist = self.CreateImageList()
        
        style = self.GetBookStyles()
        self.book = LB.LabelBook(self, wx.ID_ANY, agwStyle=style)
        
        self.SetUserColours()
        self.book.SetFontSizeMultiple(1.0)
        self.book.SetFontBold(False)
        self.book.AssignImageList(self.imagelist)
        
        global _pages
        if _pages is None:
            _pages = _lazy_import_pages()
        
        for indx, Class in enumerate(_pages):
            self.book.AddPage(Class(self.book), _pageTexts[indx], True, indx)
        
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
        style |= INB_LEFT
        style |= INB_SHOW_ONLY_TEXT
        style |= INB_SHOW_ONLY_IMAGES
        style |= INB_USE_PIN_BUTTON
        style |= INB_DRAW_SHADOW
        style |= INB_BORDER
        style |= INB_FIT_LABELTEXT
        style |= INB_BOLD_TAB_SELECTION
        
        if self.book:
            self.book.SetFontBold(1.0)
        
        return style
    
    def CreateImageList(self):
        imagelist = wx.ImageList(32, 32)
        for img in _pageIcons:
            newImg = gl.get_bitmap_path(img)
            if os.path.exists(newImg):
                bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
                imagelist.Add(bmp)
            else:
                bmp = wx.Bitmap(32, 32)
                imagelist.Add(bmp)
        return imagelist
    
    def SetUserColours(self):
        theme = gl.get_current_theme()
        
        bg_color = wx.Colour(theme.get('bg_color', '#F5F5F5'))
        active_color = wx.Colour(theme.get('panel_bg', '#FFFFFF'))
        text_color = wx.Colour(theme.get('text_color', '#333333'))
        accent_color = wx.Colour(theme.get('accent_color', '#3498DB'))
        
        self.book.SetColour(INB_TAB_AREA_BACKGROUND_COLOUR, bg_color)
        self.book.SetColour(INB_ACTIVE_TAB_COLOUR, active_color)
        self.book.SetColour(INB_TABS_BORDER_COLOUR, accent_color)
        self.book.SetColour(INB_TEXT_COLOUR, text_color)
        self.book.SetColour(INB_ACTIVE_TEXT_COLOUR, text_color)
        self.book.SetColour(INB_HILITE_TAB_COLOUR, wx.Colour(191, 216, 216))
    
    def Notify(self):
        gl.TIME_NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.SetStatusText("当前时间: " + gl.TIME_NOW, 2)


if __name__ == '__main__':
    app = wx.App(False)
    win = LabelBookDemo(parent=None)
    win.Show(True)
    app.MainLoop()
