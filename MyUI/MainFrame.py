# coding:utf-8
"""
主框架模块 - 现代化界面，支持跨平台
"""

from __future__ import print_function, unicode_literals
import wx
import wx.lib.colourselect as csel
import os
import sys
import time
import datetime

from Utils import gl

# Python 2/3 兼容性
if sys.version_info[0] == 2:
    import cStringIO
else:
    from io import BytesIO as cStringIO

# 尝试导入labelbook
try:
    from agw import labelbook as LB
    from agw.fmresources import *
except ImportError:
    import wx.lib.agw.labelbook as LB
    from wx.lib.agw.fmresources import *

from MyUI import images
from MyUI.MyNormal import MyNormal
from MyUI.MyText import MyText
from MyUI.MyWeb import MyWeb
from MyUI.MyHelp import MyHelp
from MyUI.MyAbout import MyAbout
from MyUI.MyDataImport import MyDataImport
from MyUI.MyWordFreq import MyWordFreq
from MyUI.MyBatch import MyBatch

# 页面配置
_pageTexts = [
    u"格式文件词云",
    u"文本词云生成",
    u"网页文件词云",
    u"数据导入",
    u"词频分析",
    u"批量处理",
    u"使用帮助",
    u"关于软件"
]

_pageIcons = [
    "text.png", "book.png", "web.png",
    "folder_new.png", "lbtext.png", "lbweb.png",
    "help.png", "about.png"
]

_pages = [
    MyNormal, MyText, MyWeb,
    MyDataImport, MyWordFreq, MyBatch,
    MyHelp, MyAbout
]


class LabelBookDemo(wx.Frame):
    """主窗口类"""

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.initializing = True
        self.book = None
        self._oldTextSize = 1.0
        self.current_theme = 'light'

        self.SetProperties()
        self.CreateLabelBook()
        self.DoLayout()
        self.create_menubar()
        self.create_toolbar()

        # 状态栏
        # wxPython 4 兼容性：ST_SIZEGRIP 已被移除
        try:
            statusbar = self.CreateStatusBar(3, wx.ST_SIZEGRIP)
        except AttributeError:
            statusbar = self.CreateStatusBar(3)
        statusbar.SetStatusWidths([-2, -1, -1])
        statusbar_fields = [
            u"WordCloud GUI v2.0 - 智能词云生成工具",
            u"就绪"
        ]
        for i in range(len(statusbar_fields)):
            statusbar.SetStatusText(statusbar_fields[i], i)

        # 定时器更新状态栏时间
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Notify, self.timer)
        self.timer.Start(1000)
        self.Notify()

        self.CenterOnScreen()
        self.initializing = False
        self.SendSizeEvent()
        self.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def create_menubar(self):
        """创建菜单栏"""
        menubar = wx.MenuBar()

        # 文件菜单
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, u"新建\tCtrl+N", u"新建词云项目")
        file_menu.Append(wx.ID_OPEN, u"打开文件\tCtrl+O", u"打开文本文件")
        file_menu.AppendSeparator()

        # 导入子菜单
        import_menu = wx.Menu()
        import_menu.Append(1001, u"导入TXT文件", u"导入纯文本文件")
        import_menu.Append(1002, u"导入CSV文件", u"导入CSV格式数据")
        import_menu.Append(1003, u"导入Excel文件", u"导入Excel表格数据")
        import_menu.Append(1004, u"批量导入", u"批量导入多个文件")
        file_menu.AppendSubMenu(import_menu, u"导入数据")

        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_SAVE, u"保存词云\tCtrl+S", u"保存生成的词云图片")
        file_menu.Append(1005, u"导出报告", u"导出词云分析报告")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, u"退出\tCtrl+Q", u"退出程序")

        menubar.Append(file_menu, u"文件")

        # 视图菜单
        view_menu = wx.Menu()
        self.theme_light = view_menu.AppendRadioItem(2001, u"亮色主题", u"切换到亮色主题")
        self.theme_dark = view_menu.AppendRadioItem(2002, u"暗色主题", u"切换到暗色主题")
        view_menu.AppendSeparator()
        view_menu.Append(2003, u"刷新界面\tF5", u"刷新当前界面")
        menubar.Append(view_menu, u"视图")

        # 工具菜单
        tools_menu = wx.Menu()
        tools_menu.Append(3001, u"词频分析", u"查看词频统计")
        tools_menu.Append(3002, u"批量处理", u"批量生成词云")
        tools_menu.AppendSeparator()
        tools_menu.Append(3003, u"字体管理", u"管理字体文件")
        tools_menu.Append(3004, u"停用词管理", u"管理停用词表")
        menubar.Append(tools_menu, u"工具")

        # 帮助菜单
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_HELP, u"使用帮助\tF1", u"查看使用帮助")
        help_menu.Append(4001, u"常见问题", u"查看常见问题解答")
        help_menu.AppendSeparator()
        help_menu.Append(wx.ID_ABOUT, u"关于", u"关于本软件")
        menubar.Append(help_menu, u"帮助")

        self.SetMenuBar(menubar)

        # 绑定菜单事件
        self.Bind(wx.EVT_MENU, self.OnMenuNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnThemeLight, id=2001)
        self.Bind(wx.EVT_MENU, self.OnThemeDark, id=2002)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)

        # 绑定导入菜单
        self.Bind(wx.EVT_MENU, self.OnImportTXT, id=1001)
        self.Bind(wx.EVT_MENU, self.OnImportCSV, id=1002)
        self.Bind(wx.EVT_MENU, self.OnImportExcel, id=1003)
        self.Bind(wx.EVT_MENU, self.OnBatchImport, id=1004)
        self.Bind(wx.EVT_MENU, self.OnExportReport, id=1005)

        # 绑定工具菜单
        self.Bind(wx.EVT_MENU, self.OnWordFreq, id=3001)
        self.Bind(wx.EVT_MENU, self.OnBatchProcess, id=3002)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_TEXT)

        # 添加工具按钮
        toolbar.AddTool(wx.ID_NEW, u"新建", wx.Bitmap(gl.BITMAP_DIR + "filenew.png"), wx.NullBitmap, wx.ITEM_NORMAL, u"新建项目", u"创建新的词云项目")
        toolbar.AddTool(wx.ID_OPEN, u"打开", wx.Bitmap(gl.BITMAP_DIR + "fileopen.png"), wx.NullBitmap, wx.ITEM_NORMAL, u"打开文件", u"打开文本文件")
        toolbar.AddTool(wx.ID_SAVE, u"保存", wx.Bitmap(gl.BITMAP_DIR + "filesave.png"), wx.NullBitmap, wx.ITEM_NORMAL, u"保存词云", u"保存词云图片")

        toolbar.AddSeparator()

        toolbar.AddTool(5001, u"导入数据", wx.Bitmap(gl.BITMAP_DIR + "folder_new.png"), wx.NullBitmap, wx.ITEM_NORMAL, u"导入数据", u"导入Excel/CSV/TXT文件")
        toolbar.AddTool(5002, u"词频分析", wx.Bitmap(gl.BITMAP_DIR + "lbtext.png"), wx.NullBitmap, wx.ITEM_NORMAL, u"词频分析", u"查看词频统计")
        toolbar.AddTool(5003, u"批量处理", wx.Bitmap(gl.BITMAP_DIR + "lbweb.png"), wx.NullBitmap, wx.ITEM_NORMAL, u"批量处理", u"批量生成词云")

        toolbar.Realize()

        # 绑定工具栏事件
        self.Bind(wx.EVT_TOOL, self.OnMenuNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_TOOL, self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_TOOL, self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.OnImportData, id=5001)
        self.Bind(wx.EVT_TOOL, self.OnWordFreq, id=5002)
        self.Bind(wx.EVT_TOOL, self.OnBatchProcess, id=5003)

    def SetProperties(self):
        """设置窗口属性"""
        self.icon = wx.Icon("img/logo.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        # 允许调整大小
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)

        # 设置窗口大小
        c_x, c_y, c_w, c_h = wx.ClientDisplayRect()
        print("Screen size:", c_w, c_h)

        # 默认大小，支持响应式
        self.SetSize((1000, 700))
        self.SetMinSize((800, 600))

    def DoLayout(self):
        """布局管理"""
        self.panelsizer = wx.BoxSizer(wx.VERTICAL)
        self.panelsizer.Add(self.book, 1, wx.EXPAND, 0)
        self.SetSizer(self.panelsizer)
        self.panelsizer.Layout()

    def CreateLabelBook(self, btype=0):
        """创建LabelBook"""
        if not self.initializing:
            self.Freeze()
            self.panelsizer = self.GetSizer()
            self.panelsizer.Detach(0)
            self.book.Destroy()
        else:
            self.imagelist = self.CreateImageList()

        style = self.GetBookStyles()

        self.book = LB.LabelBook(self, -1, agwStyle=style)

        self.SetUserColours()
        self.book.SetFontSizeMultiple(1.0)
        self.book.SetFontBold(False)

        self.book.AssignImageList(self.imagelist)

        for indx, Class in enumerate(_pages):
            print("Adding page:", indx, _pageTexts[indx])
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
        """获取Book样式"""
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
        """创建图像列表"""
        imagelist = wx.ImageList(32, 32)
        for img in _pageIcons:
            newImg = gl.BITMAP_DIR + "lb%s" % img
            if os.path.exists(newImg):
                bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
                imagelist.Add(bmp)
            else:
                # 使用默认空白图像
                bmp = wx.Bitmap(32, 32)
                imagelist.Add(bmp)

        return imagelist

    def SetUserColours(self):
        """设置用户颜色"""
        if self.current_theme == 'light':
            self.book.SetColour(INB_TAB_AREA_BACKGROUND_COLOUR, wx.Colour(240, 240, 240))
            self.book.SetColour(INB_ACTIVE_TAB_COLOUR, wx.Colour(255, 255, 255))
            self.book.SetColour(INB_TABS_BORDER_COLOUR, wx.Colour(200, 200, 200))
            self.book.SetColour(INB_TEXT_COLOUR, wx.Colour(50, 50, 50))
            self.book.SetColour(INB_ACTIVE_TEXT_COLOUR, wx.Colour(0, 120, 215))
            self.book.SetColour(INB_HILITE_TAB_COLOUR, wx.Colour(230, 230, 230))
        else:
            self.book.SetColour(INB_TAB_AREA_BACKGROUND_COLOUR, wx.Colour(45, 45, 48))
            self.book.SetColour(INB_ACTIVE_TAB_COLOUR, wx.Colour(37, 37, 38))
            self.book.SetColour(INB_TABS_BORDER_COLOUR, wx.Colour(62, 62, 66))
            self.book.SetColour(INB_TEXT_COLOUR, wx.Colour(204, 204, 204))
            self.book.SetColour(INB_ACTIVE_TEXT_COLOUR, wx.Colour(0, 151, 251))
            self.book.SetColour(INB_HILITE_TAB_COLOUR, wx.Colour(62, 62, 66))

    def Notify(self, event=None):
        """状态栏时间更新"""
        gl.TIME_NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.SetStatusText(u"当前时间: " + gl.TIME_NOW, 2)

    def OnPageChanged(self, event):
        """页面切换事件"""
        page_idx = event.GetSelection()
        print("Page changed to:", page_idx)

        # 通知当前页面更新
        try:
            current_page = self.book.GetCurrentPage()
            if hasattr(current_page, 'update_Choice'):
                current_page.update_Choice()
            if hasattr(current_page, 'on_page_active'):
                current_page.on_page_active()
        except Exception as e:
            print("Page update error:", e)

        event.Skip()

    # 菜单事件处理
    def OnMenuNew(self, event):
        """新建项目"""
        dlg = wx.MessageDialog(self, u"新建项目将清空当前内容，是否继续？", u"确认", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            # 清空当前内容
            pass
        dlg.Destroy()

    def OnMenuOpen(self, event):
        """打开文件"""
        wildcard = u"文本文件 (*.txt)|*.txt|所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(self, u"选择文件", gl.CWD, "", wildcard, wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            # 切换到文本词云页面并加载文件
            self.book.SetSelection(1)  # MyText页面
            page = self.book.GetCurrentPage()
            if hasattr(page, 'load_file'):
                page.load_file(filepath)
        dlg.Destroy()

    def OnMenuSave(self, event):
        """保存词云"""
        # 获取当前页面
        page = self.book.GetCurrentPage()
        if hasattr(page, 'save_wordcloud'):
            page.save_wordcloud()
        else:
            wx.MessageBox(u"当前页面不支持保存词云", u"提示", wx.OK | wx.ICON_INFORMATION)

    def OnMenuExit(self, event):
        """退出程序"""
        self.Close()

    def OnThemeLight(self, event):
        """亮色主题"""
        self.current_theme = 'light'
        self.SetUserColours()
        self.book.Refresh()
        wx.MessageBox(u"已切换到亮色主题", u"主题切换", wx.OK | wx.ICON_INFORMATION)

    def OnThemeDark(self, event):
        """暗色主题"""
        self.current_theme = 'dark'
        self.SetUserColours()
        self.book.Refresh()
        wx.MessageBox(u"已切换到暗色主题", u"主题切换", wx.OK | wx.ICON_INFORMATION)

    def OnHelp(self, event):
        """帮助"""
        self.book.SetSelection(6)  # MyHelp页面

    def OnAbout(self, event):
        """关于"""
        self.book.SetSelection(7)  # MyAbout页面

    def OnImportTXT(self, event):
        """导入TXT"""
        self.book.SetSelection(3)  # MyDataImport页面
        page = self.book.GetCurrentPage()
        if hasattr(page, 'set_import_type'):
            page.set_import_type('txt')

    def OnImportCSV(self, event):
        """导入CSV"""
        self.book.SetSelection(3)
        page = self.book.GetCurrentPage()
        if hasattr(page, 'set_import_type'):
            page.set_import_type('csv')

    def OnImportExcel(self, event):
        """导入Excel"""
        self.book.SetSelection(3)
        page = self.book.GetCurrentPage()
        if hasattr(page, 'set_import_type'):
            page.set_import_type('excel')

    def OnBatchImport(self, event):
        """批量导入"""
        self.book.SetSelection(3)
        page = self.book.GetCurrentPage()
        if hasattr(page, 'set_batch_mode'):
            page.set_batch_mode(True)

    def OnImportData(self, event):
        """导入数据"""
        self.book.SetSelection(3)

    def OnExportReport(self, event):
        """导出报告"""
        page = self.book.GetCurrentPage()
        if hasattr(page, 'export_report'):
            page.export_report()
        else:
            wx.MessageBox(u"请在词云生成页面导出报告", u"提示", wx.OK | wx.ICON_INFORMATION)

    def OnWordFreq(self, event):
        """词频分析"""
        self.book.SetSelection(4)  # MyWordFreq页面

    def OnBatchProcess(self, event):
        """批量处理"""
        self.book.SetSelection(5)  # MyBatch页面


if __name__ == '__main__':
    app = wx.App(False)
    win = LabelBookDemo(parent=None)
    win.Show(True)
    app.MainLoop()
