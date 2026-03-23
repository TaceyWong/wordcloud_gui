# coding:utf-8
"""
主界面框架
增强版：支持主题切换、跨平台兼容、新增功能入口
"""
__author__ = 'Tacey Wong & AI Assistant'
__date__ = "2024年"

import wx
import wx.lib.colourselect as csel
import random
import os
import sys
import time
import datetime

from Utils import gl

from .MyNormal import *
from .MyText import *
from .MyWeb import *
from .MyHelp import *
from .MyAbout import *
from .MyEnhanced import *

try:
    from agw import labelbook as LB
    from agw.fmresources import *
except ImportError:
    import wx.lib.agw.labelbook as LB
    from wx.lib.agw.fmresources import *

from . import images

# 跨平台路径处理
def get_platform_path(path):
    return os.path.normpath(path)

# 主题定义
class Theme:
    LIGHT = 0
    DARK = 1

class ThemeColors:
    @staticmethod
    def get_light_theme():
        return {
            'bg': wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK),
            'text': wx.BLACK,
            'panel': wx.WHITE,
            'highlight': wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT),
            'button': wx.Colour(100, 200, 100),
            'tab_area': wx.Colour(132, 164, 213),
            'active_tab': wx.WHITE,
            'border': wx.Colour(0, 0, 204),
            'hilite_tab': wx.Colour(191, 216, 216)
        }
    
    @staticmethod
    def get_dark_theme():
        return {
            'bg': wx.Colour(45, 45, 48),
            'text': wx.WHITE,
            'panel': wx.Colour(30, 30, 30),
            'highlight': wx.Colour(0, 122, 255),
            'button': wx.Colour(50, 150, 50),
            'tab_area': wx.Colour(60, 60, 65),
            'active_tab': wx.Colour(45, 45, 48),
            'border': wx.Colour(80, 80, 85),
            'hilite_tab': wx.Colour(70, 70, 75)
        }

_pageTexts = [u"增强版词云生成", u"格式文件词云生成", u"文本词云生成", u"网页词云生成", u"使用帮助", u"关于本软件"]
_pageIcons = ["text.png", "book.png", "text.png", "web.png", "help.png", "about.png"]
_pages = [MyEnhanced, MyNormal, MyText, MyWeb, MyHelp, MyAbout]

class LabelBookDemo(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        
        self.initializing = True
        self.book = None
        self._oldTextSize = 1.0
        self.current_theme = Theme.LIGHT
        self.theme_colors = ThemeColors.get_light_theme()
        
        # 初始化全局路径
        gl.CWD = os.getcwd()
        gl.BITMAP_DIR = get_platform_path('bitmaps/')
        
        # 创建缓存目录
        self.create_cache_dir()
        
        self.SetProperties()
        self.CreateLabelBook()
        self.DoLayout()
        self.create_menubar()
        self.create_toolbar()
        
        # 窗口底部状态栏
        statusbar = self.CreateStatusBar(3, wx.STB_SIZEGRIP)
        statusbar.SetStatusWidths([-3, -2, -1])
        statusbar_fields = [(u"WordCloud-Gui 增强版 - 词云生成GUI软件"),
                            (u"支持多数据源导入 | 词频统计 | 批量处理"),
                            (u"")]
        for i in range(len(statusbar_fields)):
            statusbar.SetStatusText(statusbar_fields[i], i)
        
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()
        
        self.CenterOnScreen()
        self.initializing = False
        self.SendSizeEvent()
        self.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
    
    def create_cache_dir(self):
        """创建缓存目录"""
        cache_dir = get_platform_path(os.path.join(gl.CWD, "data", ".catch"))
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        gl.CACHE_DIR = cache_dir
    
    def create_menubar(self):
        """创建菜单栏"""
        menu_data = [
            ("&文件", (
                ("&新建", "新建词云项目", self.OnNew),
                ("&打开", "打开数据文件", self.OnOpen),
                (" & 保存", "保存词云图片", self.OnSave), 
                ("", "", ""),
                ("批量处理", "批量生成词云", self.OnBatchProcess),
                ("", "", ""),
                ("&退出", "退出程序", self.OnExit)
            )),
            ("&编辑", (
                ("&数据导入", "导入数据文件", self.OnImportData),
                ("词频分析", "查看词频统计", self.OnWordFreq),
                ("", "", ""),
                ("&参数设置", "词云参数设置", self.OnSettings)
            )),
            ("&视图", (
                ("&切换主题", "切换暗色/亮色主题", self.OnToggleTheme),
                ("", "", ""),
                ("&放大", "放大界面", self.OnZoomIn),
                ("&缩小", "缩小界面", self.OnZoomOut)
            )),
            ("&帮助", (
                ("&使用帮助", "查看使用帮助", self.OnHelp),
                ("&常见问题", "常见问题解答", self.OnFAQ),
                ("", "", ""),
                ("&关于", "关于软件", self.OnAbout)
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
                menu.AppendMenu(wx.NewId(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu
    
    def createMenuItem(self, menu, label, status, handler, kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1, label, status, kind)
        self.Bind(wx.EVT_MENU, handler, menuItem)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        
        # 添加工具按钮
        new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (16, 16))
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16, 16))
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (16, 16))
        refresh_bmp = wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR, (16, 16))
        chart_bmp = wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_TOOLBAR, (16, 16))
        
        toolbar.AddTool(wx.ID_NEW, "新建", new_bmp, "新建项目")
        toolbar.AddTool(wx.ID_OPEN, "打开", open_bmp, "打开文件")
        toolbar.AddTool(wx.ID_SAVE, "保存", save_bmp, "保存词云")
        toolbar.AddSeparator()
        toolbar.AddTool(wx.ID_REFRESH, "刷新", refresh_bmp, "重新生成")
        toolbar.AddTool(wx.ID_REPLACE, "词频统计", chart_bmp, "查看词频统计")
        toolbar.AddSeparator()
        
        # 主题切换按钮
        theme_bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_TOOLBAR, (16, 16))
        toolbar.AddTool(wx.ID_PREFERENCES, "切换主题", theme_bmp, "切换暗色/亮色主题")
        
        toolbar.Realize()
        
        # 绑定工具栏事件
        self.Bind(wx.EVT_TOOL, self.OnNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.OnRefresh, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_TOOL, self.OnWordFreq, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_TOOL, self.OnToggleTheme, id=wx.ID_PREFERENCES)
    
    def OnNew(self, event):
        """新建项目"""
        self.book.SetSelection(0)
        wx.MessageBox("可以开始创建新的词云项目了！", "提示", wx.OK | wx.ICON_INFORMATION)
    
    def OnOpen(self, event):
        """打开文件"""
        self.book.SetSelection(0)
        current_page = self.book.GetCurrentPage()
        if hasattr(current_page, 'on_single_file'):
            current_page.on_single_file(None)
    
    def OnSave(self, event):
        """保存"""
        current_page = self.book.GetCurrentPage()
        if hasattr(current_page, 'final_pic') and current_page.final_pic is not None:
            if hasattr(current_page, 'on_export_image'):
                current_page.on_export_image(None)
            elif hasattr(current_page, 'Save_ButtonOnButtonClick'):
                current_page.Save_ButtonOnButtonClick(None)
        else:
            wx.MessageBox("请先生成词云！", "提示", wx.OK | wx.ICON_INFORMATION)
    
    def OnExit(self, event):
        """退出程序"""
        self.Close()
    
    def OnBatchProcess(self, event):
        """批量处理"""
        self.book.SetSelection(0)
        wx.MessageBox("请在增强版面板中选择多个文件后使用批量导出功能！", "提示", wx.OK | wx.ICON_INFORMATION)
    
    def OnImportData(self, event):
        """导入数据"""
        self.book.SetSelection(0)
        self.OnOpen(event)
    
    def OnWordFreq(self, event):
        """词频分析"""
        self.book.SetSelection(0)
        current_page = self.book.GetCurrentPage()
        if hasattr(current_page, 'on_show_freq'):
            current_page.on_show_freq(None)
        else:
            wx.MessageBox("请先生成词云后再查看词频统计！", "提示", wx.OK | wx.ICON_INFORMATION)
    
    def OnSettings(self, event):
        """参数设置"""
        self.book.SetSelection(0)
        self.notebook.ChangeSelection(1)
    
    def OnToggleTheme(self, event):
        """切换主题"""
        if self.current_theme == Theme.LIGHT:
            self.current_theme = Theme.DARK
            self.theme_colors = ThemeColors.get_dark_theme()
        else:
            self.current_theme = Theme.LIGHT
            self.theme_colors = ThemeColors.get_light_theme()
        
        self.ApplyTheme()
    
    def ApplyTheme(self):
        """应用主题"""
        self.SetBackgroundColour(self.theme_colors['bg'])
        
        if self.book:
            self.book.SetColour(INB_TAB_AREA_BACKGROUND_COLOUR, self.theme_colors['tab_area'])
            self.book.SetColour(INB_ACTIVE_TAB_COLOUR, self.theme_colors['active_tab'])
            self.book.SetColour(INB_TABS_BORDER_COLOUR, self.theme_colors['border'])
            self.book.SetColour(INB_TEXT_COLOUR, self.theme_colors['text'])
            self.book.SetColour(INB_ACTIVE_TEXT_COLOUR, self.theme_colors['text'])
            self.book.SetColour(INB_HILITE_TAB_COLOUR, self.theme_colors['hilite_tab'])
        
        for i in range(self.book.GetPageCount()):
            page = self.book.GetPage(i)
            page.SetBackgroundColour(self.theme_colors['bg'])
        
        self.Refresh()
    
    def OnZoomIn(self, event):
        """放大界面"""
        if self.book:
            current_size = self.book.GetFontSizeMultiple()
            self.book.SetFontSizeMultiple(min(current_size + 0.1, 2.0))
    
    def OnZoomOut(self, event):
        """缩小界面"""
        if self.book:
            current_size = self.book.GetFontSizeMultiple()
            self.book.SetFontSizeMultiple(max(current_size - 0.1, 0.5))
    
    def OnHelp(self, event):
        """帮助"""
        self.book.SetSelection(4)
    
    def OnFAQ(self, event):
        """常见问题"""
        faq_text = """常见问题解答：

Q: 中文显示乱码怎么办？
A: 请在字体设置中选择支持中文的字体（如 simsun）。

Q: 支持哪些文件格式？
A: 支持 TXT、CSV、Excel（XLS/XLSX）格式的文件导入。

Q: 如何自定义形状？
A: 在词云配置中选择蒙版图片（支持 PNG/JPG/BMP 格式）。

Q: 如何添加自定义词典？
A: 在数据导入面板选择自定义词典文件（TXT 格式，每行一个词）。

Q: 支持哪些导出格式？
A: 支持导出为 PNG/JPG/PDF/SVG 图片格式，以及 PDF/Markdown 报告。
"""
        wx.MessageBox(faq_text, "常见问题", wx.OK | wx.ICON_INFORMATION)
    
    def OnAbout(self, event):
        """关于"""
        self.book.SetSelection(5)
    
    def OnRefresh(self, event):
        """刷新"""
        current_page = self.book.GetCurrentPage()
        if hasattr(current_page, 'on_preview'):
            current_page.on_preview(None)
    
    def OnPageChanged(self, event):
        """页面切换事件"""
        event.Skip()
        selection = event.GetSelection()
        if hasattr(self.book.GetCurrentPage(), 'update_Choice'):
            self.book.GetCurrentPage().update_Choice()
    
    def SetProperties(self):
        """设置窗口属性"""
        self.icon = wx.Icon(get_platform_path("img/logo.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        
        # 允许窗口调整大小
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        
        # 设置最小窗口大小
        self.SetSizeHints(800, 600)
        self.SetSize((950, 700))
    
    def DoLayout(self):
        """布局"""
        self.panelsizer = wx.BoxSizer(wx.VERTICAL)
        self.panelsizer.Add(self.book, 1, wx.EXPAND, 0)
        self.SetSizer(self.panelsizer)
        self.panelsizer.Layout()
        self.Layout()
    
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
        """获取LabelBook样式"""
        style = INB_FIT_BUTTON
        style |= INB_LEFT
        style |= INB_SHOW_ONLY_TEXT
        style |= INB_SHOW_ONLY_IMAGES
        style |= INB_USE_PIN_BUTTON
        style |= INB_DRAW_SHADOW
        style |= INB_BORDER
        style |= INB_FIT_LABELTEXT
        style |= INB_BOLD_TAB_SELECTION
        
        return style
    
    def CreateImageList(self):
        """创建图标列表"""
        imagelist = wx.ImageList(32, 32)
        for img in _pageIcons:
            newImg = get_platform_path(gl.BITMAP_DIR + "lb%s" % img)
            if os.path.exists(newImg):
                bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
            else:
                bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (32, 32))
            imagelist.Add(bmp)
        
        return imagelist
    
    def OnBookType(self, event):
        self.CreateLabelBook(event.GetInt())
        event.Skip()
    
    def SetUserColours(self):
        """设置颜色"""
        self.book.SetColour(INB_TAB_AREA_BACKGROUND_COLOUR, self.theme_colors['tab_area'])
        self.book.SetColour(INB_ACTIVE_TAB_COLOUR, self.theme_colors['active_tab'])
        self.book.SetColour(INB_TABS_BORDER_COLOUR, self.theme_colors['border'])
        self.book.SetColour(INB_TEXT_COLOUR, self.theme_colors['text'])
        self.book.SetColour(INB_ACTIVE_TEXT_COLOUR, self.theme_colors['text'])
        self.book.SetColour(INB_HILITE_TAB_COLOUR, self.theme_colors['hilite_tab'])
    
    def Notify(self):
        """更新时间显示"""
        gl.TIME_NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.SetStatusText(u"当前时间：" + gl.TIME_NOW, 2)


if __name__ == '__main__':
    app = wx.App(False)
    win = LabelBookDemo(parent=None)
    win.Show(True)
    app.MainLoop()
