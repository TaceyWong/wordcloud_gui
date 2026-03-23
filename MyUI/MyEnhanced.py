# coding:utf-8
"""
增强版词云生成主界面
整合数据导入、词云生成、词频分析、导出等功能
"""
import wx
import wx.lib.scrolledpanel as scrolled
import os
import io
from PIL import Image

from Utils import gl
from Utils.new_wordcloud import MyWordCloud
from Utils.data_processor import DataProcessor
from Utils.exporter import Exporter
from Utils.visualizer import Visualizer


class MyEnhanced(wx.Panel):
    """增强版词云生成面板"""
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        
        # 初始化变量
        self.stop_word_file = None
        self.goal_files = []
        self.mask_file = None
        self.custom_dict_file = None
        self.final_pic = None
        self.word_freq = []
        self.my_wordcloud = MyWordCloud()
        self.data_processor = DataProcessor()
        self.exporter = Exporter()
        self.visualizer = Visualizer()
        self.current_mask = None
        
        # 支持的文件格式
        self.supported_formats = {
            'txt': 'TXT文本文件 (*.txt)|*.txt',
            'csv': 'CSV文件 (*.csv)|*.csv',
            'excel': 'Excel文件 (*.xls;*.xlsx)|*.xls;*.xlsx',
            'all': '所有支持的格式 (*.txt;*.csv;*.xls;*.xlsx)|*.txt;*.csv;*.xls;*.xlsx'
        }
        
        # 颜色方案
        self.colormaps = MyWordCloud.get_available_colormaps()[:30]
        
        # 创建界面
        self.create_ui()
        
        # 绑定事件
        self.bind_events()
        
        # 更新字体列表
        self.update_font_choice()
    
    def create_ui(self):
        """创建UI界面"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建笔记本控件
        self.notebook = wx.Notebook(self, wx.ID_ANY)
        
        # 1. 数据导入面板
        self.data_panel = self.create_data_panel()
        self.notebook.AddPage(self.data_panel, "数据导入")
        
        # 2. 词云配置面板
        self.config_panel = self.create_config_panel()
        self.notebook.AddPage(self.config_panel, "词云配置")
        
        # 3. 生成与预览面板
        self.preview_panel = self.create_preview_panel()
        self.notebook.AddPage(self.preview_panel, "生成与预览")
        
        # 4. 导出面板
        self.export_panel = self.create_export_panel()
        self.notebook.AddPage(self.export_panel, "导出")
        
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)
        self.Layout()
    
    def create_data_panel(self):
        """创建数据导入面板"""
        panel = scrolled.ScrolledPanel(self.notebook, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        panel.SetAutoLayout(True)
        panel.SetupScrolling()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 数据源组
        source_box = wx.StaticBox(panel, wx.ID_ANY, "数据源选择")
        source_sizer = wx.StaticBoxSizer(source_box, wx.VERTICAL)
        
        # 单个文件导入
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.single_file_btn = wx.Button(panel, wx.ID_ANY, "导入文件", size=(100, 30))
        file_sizer.Add(self.single_file_btn, 0, wx.ALL, 5)
        self.single_file_text = wx.StaticText(panel, wx.ID_ANY, "当前：无文件选择")
        self.single_file_text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        file_sizer.Add(self.single_file_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        source_sizer.Add(file_sizer, 0, wx.EXPAND)
        
        # 批量文件导入
        batch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.batch_file_btn = wx.Button(panel, wx.ID_ANY, "批量导入", size=(100, 30))
        batch_sizer.Add(self.batch_file_btn, 0, wx.ALL, 5)
        self.batch_file_text = wx.StaticText(panel, wx.ID_ANY, "已选择：0个文件")
        self.batch_file_text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        batch_sizer.Add(self.batch_file_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        source_sizer.Add(batch_sizer, 0, wx.EXPAND)
        
        sizer.Add(source_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 文本处理配置组
        process_box = wx.StaticBox(panel, wx.ID_ANY, "文本处理配置")
        process_sizer = wx.StaticBoxSizer(process_box, wx.VERTICAL)
        
        # 停用词表
        stopword_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.stopword_btn = wx.Button(panel, wx.ID_ANY, "停用词表", size=(100, 30))
        stopword_sizer.Add(self.stopword_btn, 0, wx.ALL, 5)
        self.stopword_text = wx.StaticText(panel, wx.ID_ANY, "当前：默认中文停用词")
        self.stopword_text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        stopword_sizer.Add(self.stopword_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        process_sizer.Add(stopword_sizer, 0, wx.EXPAND)
        
        # 自定义词典
        dict_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dict_btn = wx.Button(panel, wx.ID_ANY, "自定义词典", size=(100, 30))
        dict_sizer.Add(self.dict_btn, 0, wx.ALL, 5)
        self.dict_text = wx.StaticText(panel, wx.ID_ANY, "当前：无自定义词典")
        self.dict_text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        dict_sizer.Add(self.dict_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        process_sizer.Add(dict_sizer, 0, wx.EXPAND)
        
        # 语言选择
        lang_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_label = wx.StaticText(panel, wx.ID_ANY, "语言：")
        lang_sizer.Add(lang_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lang_choice = wx.Choice(panel, wx.ID_ANY, choices=["中文", "英文"])
        self.lang_choice.SetSelection(0)
        lang_sizer.Add(self.lang_choice, 0, wx.ALL, 5)
        process_sizer.Add(lang_sizer, 0, wx.EXPAND)
        
        sizer.Add(process_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 清洗选项
        clean_box = wx.StaticBox(panel, wx.ID_ANY, "文本清洗选项")
        clean_sizer = wx.StaticBoxSizer(clean_box, wx.VERTICAL)
        
        self.clean_punct = wx.CheckBox(panel, wx.ID_ANY, "去除标点符号")
        self.clean_punct.SetValue(True)
        clean_sizer.Add(self.clean_punct, 0, wx.ALL, 5)
        
        self.clean_numbers = wx.CheckBox(panel, wx.ID_ANY, "去除数字")
        self.clean_numbers.SetValue(True)
        clean_sizer.Add(self.clean_numbers, 0, wx.ALL, 5)
        
        self.clean_special = wx.CheckBox(panel, wx.ID_ANY, "去除特殊字符")
        self.clean_special.SetValue(True)
        clean_sizer.Add(self.clean_special, 0, wx.ALL, 5)
        
        sizer.Add(clean_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 处理按钮
        self.process_btn = wx.Button(panel, wx.ID_ANY, "开始处理文本", size=(200, 40))
        self.process_btn.SetBackgroundColour(wx.Colour(100, 200, 100))
        sizer.Add(self.process_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def create_config_panel(self):
        """创建设置面板"""
        panel = scrolled.ScrolledPanel(self.notebook, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        panel.SetAutoLayout(True)
        panel.SetupScrolling()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 基本设置
        basic_box = wx.StaticBox(panel, wx.ID_ANY, "基本设置")
        basic_sizer = wx.StaticBoxSizer(basic_box, wx.VERTICAL)
        
        # 尺寸设置
        size_grid = wx.FlexGridSizer(0, 4, 5, 5)
        size_grid.Add(wx.StaticText(panel, wx.ID_ANY, "宽度："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.width_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="800", min=200, max=4000)
        size_grid.Add(self.width_spin, 0)
        
        size_grid.Add(wx.StaticText(panel, wx.ID_ANY, "高度："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.height_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="600", min=200, max=4000)
        size_grid.Add(self.height_spin, 0)
        
        size_grid.Add(wx.StaticText(panel, wx.ID_ANY, "边距："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.margin_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="2", min=0, max=100)
        size_grid.Add(self.margin_spin, 0)
        
        size_grid.Add(wx.StaticText(panel, wx.ID_ANY, "缩放："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.scale_spin = wx.SpinCtrlDouble(panel, wx.ID_ANY, value="1.0", min=0.5, max=3.0, inc=0.1)
        size_grid.Add(self.scale_spin, 0)
        
        basic_sizer.Add(size_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        sizer.Add(basic_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 字体设置
        font_box = wx.StaticBox(panel, wx.ID_ANY, "字体设置")
        font_sizer = wx.StaticBoxSizer(font_box, wx.VERTICAL)
        
        font_grid = wx.FlexGridSizer(0, 4, 5, 5)
        font_grid.Add(wx.StaticText(panel, wx.ID_ANY, "字体："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.font_choice = wx.Choice(panel, wx.ID_ANY, choices=[])
        font_grid.Add(self.font_choice, 0)
        
        font_grid.Add(wx.StaticText(panel, wx.ID_ANY, "最小字号："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.min_font_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="4", min=1, max=100)
        font_grid.Add(self.min_font_spin, 0)
        
        font_grid.Add(wx.StaticText(panel, wx.ID_ANY, "最大字号："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.max_font_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="None", min=0, max=200)
        font_grid.Add(self.max_font_spin, 0)
        
        font_grid.Add(wx.StaticText(panel, wx.ID_ANY, "横向偏好："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.horiz_spin = wx.SpinCtrlDouble(panel, wx.ID_ANY, value="0.9", min=0, max=1, inc=0.1)
        font_grid.Add(self.horiz_spin, 0)
        
        font_sizer.Add(font_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        sizer.Add(font_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 颜色和样式
        style_box = wx.StaticBox(panel, wx.ID_ANY, "颜色和样式")
        style_sizer = wx.StaticBoxSizer(style_box, wx.VERTICAL)
        
        style_grid = wx.FlexGridSizer(0, 4, 5, 5)
        style_grid.Add(wx.StaticText(panel, wx.ID_ANY, "背景色："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.bg_color_picker = wx.ColourPickerCtrl(panel, wx.ID_ANY, wx.WHITE)
        style_grid.Add(self.bg_color_picker, 0)
        
        style_grid.Add(wx.StaticText(panel, wx.ID_ANY, "颜色方案："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.colormap_choice = wx.Choice(panel, wx.ID_ANY, choices=self.colormaps)
        self.colormap_choice.SetSelection(0)
        style_grid.Add(self.colormap_choice, 0)
        
        style_sizer.Add(style_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        # 蒙版设置
        mask_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mask_btn = wx.Button(panel, wx.ID_ANY, "选择蒙版图片", size=(120, 30))
        mask_sizer.Add(self.mask_btn, 0, wx.ALL, 5)
        self.mask_text = wx.StaticText(panel, wx.ID_ANY, "当前：无蒙版")
        self.mask_text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        mask_sizer.Add(self.mask_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.use_mask_color = wx.CheckBox(panel, wx.ID_ANY, "使用蒙版图片颜色")
        mask_sizer.Add(self.use_mask_color, 0, wx.ALL, 5)
        
        style_sizer.Add(mask_sizer, 0, wx.EXPAND)
        
        sizer.Add(style_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 高级设置
        advanced_box = wx.StaticBox(panel, wx.ID_ANY, "高级设置")
        advanced_sizer = wx.StaticBoxSizer(advanced_box, wx.VERTICAL)
        
        advanced_grid = wx.FlexGridSizer(0, 4, 5, 5)
        advanced_grid.Add(wx.StaticText(panel, wx.ID_ANY, "最大词数："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.max_words_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="200", min=10, max=1000)
        advanced_grid.Add(self.max_words_spin, 0)
        
        advanced_sizer.Add(advanced_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        sizer.Add(advanced_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def create_preview_panel(self):
        """创建预览面板"""
        panel = wx.Panel(self.notebook, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 工具栏
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.generate_btn = wx.Button(panel, wx.ID_ANY, "生成词云", size=(120, 40))
        self.generate_btn.SetBackgroundColour(wx.Colour(100, 200, 100))
        toolbar_sizer.Add(self.generate_btn, 0, wx.ALL, 5)
        
        self.preview_btn = wx.Button(panel, wx.ID_ANY, "实时预览", size=(120, 40))
        toolbar_sizer.Add(self.preview_btn, 0, wx.ALL, 5)
        
        self.show_freq_btn = wx.Button(panel, wx.ID_ANY, "显示词频统计", size=(120, 40))
        toolbar_sizer.Add(self.show_freq_btn, 0, wx.ALL, 5)
        
        sizer.Add(toolbar_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 预览区域
        preview_box = wx.StaticBox(panel, wx.ID_ANY, "词云预览")
        preview_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)
        
        self.preview_bitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.NullBitmap)
        preview_sizer.Add(self.preview_bitmap, 1, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(preview_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        return panel
    
    def create_export_panel(self):
        """创建导出面板"""
        panel = wx.Panel(self.notebook, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 图片导出
        img_box = wx.StaticBox(panel, wx.ID_ANY, "图片导出")
        img_sizer = wx.StaticBoxSizer(img_box, wx.VERTICAL)
        
        img_grid = wx.FlexGridSizer(0, 3, 5, 5)
        img_grid.Add(wx.StaticText(panel, wx.ID_ANY, "格式："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.img_format_choice = wx.Choice(panel, wx.ID_ANY, choices=["PNG", "JPG", "PDF", "SVG"])
        self.img_format_choice.SetSelection(0)
        img_grid.Add(self.img_format_choice, 0)
        
        img_grid.Add(wx.StaticText(panel, wx.ID_ANY, "DPI："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.dpi_spin = wx.SpinCtrl(panel, wx.ID_ANY, value="300", min=72, max=600)
        img_grid.Add(self.dpi_spin, 0)
        
        img_sizer.Add(img_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        self.export_img_btn = wx.Button(panel, wx.ID_ANY, "导出图片", size=(120, 40))
        img_sizer.Add(self.export_img_btn, 0, wx.ALL, 5)
        
        sizer.Add(img_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 报告导出
        report_box = wx.StaticBox(panel, wx.ID_ANY, "报告导出")
        report_sizer = wx.StaticBoxSizer(report_box, wx.VERTICAL)
        
        report_grid = wx.FlexGridSizer(0, 2, 5, 5)
        report_grid.Add(wx.StaticText(panel, wx.ID_ANY, "格式："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.report_format_choice = wx.Choice(panel, wx.ID_ANY, choices=["PDF", "Markdown"])
        self.report_format_choice.SetSelection(0)
        report_grid.Add(self.report_format_choice, 0)
        
        report_sizer.Add(report_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        self.export_report_btn = wx.Button(panel, wx.ID_ANY, "生成报告", size=(120, 40))
        report_sizer.Add(self.export_report_btn, 0, wx.ALL, 5)
        
        sizer.Add(report_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 数据导出
        data_box = wx.StaticBox(panel, wx.ID_ANY, "数据导出")
        data_sizer = wx.StaticBoxSizer(data_box, wx.VERTICAL)
        
        data_grid = wx.FlexGridSizer(0, 2, 5, 5)
        data_grid.Add(wx.StaticText(panel, wx.ID_ANY, "格式："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.data_format_choice = wx.Choice(panel, wx.ID_ANY, choices=["CSV", "Excel"])
        self.data_format_choice.SetSelection(0)
        data_grid.Add(self.data_format_choice, 0)
        
        data_sizer.Add(data_grid, 0, wx.EXPAND | wx.ALL, 10)
        
        self.export_data_btn = wx.Button(panel, wx.ID_ANY, "导出词频数据", size=(120, 40))
        data_sizer.Add(self.export_data_btn, 0, wx.ALL, 5)
        
        sizer.Add(data_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 批量处理
        batch_box = wx.StaticBox(panel, wx.ID_ANY, "批量处理")
        batch_sizer = wx.StaticBoxSizer(batch_box, wx.VERTICAL)
        
        self.batch_export_btn = wx.Button(panel, wx.ID_ANY, "批量生成词云", size=(120, 40))
        batch_sizer.Add(self.batch_export_btn, 0, wx.ALL, 5)
        
        sizer.Add(batch_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def bind_events(self):
        """绑定事件"""
        # 数据导入
        self.single_file_btn.Bind(wx.EVT_BUTTON, self.on_single_file)
        self.batch_file_btn.Bind(wx.EVT_BUTTON, self.on_batch_file)
        self.stopword_btn.Bind(wx.EVT_BUTTON, self.on_stopword)
        self.dict_btn.Bind(wx.EVT_BUTTON, self.on_custom_dict)
        self.process_btn.Bind(wx.EVT_BUTTON, self.on_process_text)
        
        # 词云配置
        self.mask_btn.Bind(wx.EVT_BUTTON, self.on_mask)
        
        # 生成与预览
        self.generate_btn.Bind(wx.EVT_BUTTON, self.on_generate)
        self.preview_btn.Bind(wx.EVT_BUTTON, self.on_preview)
        self.show_freq_btn.Bind(wx.EVT_BUTTON, self.on_show_freq)
        
        # 导出
        self.export_img_btn.Bind(wx.EVT_BUTTON, self.on_export_image)
        self.export_report_btn.Bind(wx.EVT_BUTTON, self.on_export_report)
        self.export_data_btn.Bind(wx.EVT_BUTTON, self.on_export_data)
        self.batch_export_btn.Bind(wx.EVT_BUTTON, self.on_batch_export)
    
    def update_font_choice(self):
        """更新字体列表"""
        font_dir = os.path.join(gl.CWD, "data", "font")
        if os.path.exists(font_dir):
            fonts = []
            for f in os.listdir(font_dir):
                if f.lower().endswith(".ttf"):
                    fonts.append(os.path.splitext(f)[0])
            self.font_choice.Clear()
            self.font_choice.AppendItems(fonts)
            if fonts:
                self.font_choice.SetSelection(0)
    
    def on_single_file(self, event):
        """单个文件导入"""
        wildcard = self.supported_formats['all']
        dlg = wx.FileDialog(self, message="选择数据文件", defaultDir=gl.CWD,
                           wildcard=wildcard, style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.goal_files = [path]
            self.single_file_text.SetLabelText(f"当前：{os.path.basename(path)}")
            self.batch_file_text.SetLabelText(f"已选择：1个文件")
        
        dlg.Destroy()
    
    def on_batch_file(self, event):
        """批量文件导入"""
        wildcard = self.supported_formats['all']
        dlg = wx.FileDialog(self, message="选择多个数据文件", defaultDir=gl.CWD,
                           wildcard=wildcard, style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_MULTIPLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.goal_files = paths
            self.single_file_text.SetLabelText(f"当前：{os.path.basename(paths[0])}...")
            self.batch_file_text.SetLabelText(f"已选择：{len(paths)}个文件")
        
        dlg.Destroy()
    
    def on_stopword(self, event):
        """选择停用词表"""
        wildcard = "TXT文件 (*.txt)|*.txt"
        default_dir = os.path.join(gl.CWD, "data", "stopwords")
        dlg = wx.FileDialog(self, message="选择停用词表", defaultDir=default_dir,
                           wildcard=wildcard, style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.stop_word_file = path
            self.stopword_text.SetLabelText(f"当前：{os.path.basename(path)}")
        
        dlg.Destroy()
    
    def on_custom_dict(self, event):
        """选择自定义词典"""
        wildcard = "TXT文件 (*.txt)|*.txt"
        dlg = wx.FileDialog(self, message="选择自定义词典", defaultDir=gl.CWD,
                           wildcard=wildcard, style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.custom_dict_file = path
            self.dict_text.SetLabelText(f"当前：{os.path.basename(path)}")
        
        dlg.Destroy()
    
    def on_mask(self, event):
        """选择蒙版图片"""
        wildcard = "图片文件 (*.png;*.jpg;*.jpeg;*.bmp)|*.png;*.jpg;*.jpeg;*.bmp"
        dlg = wx.FileDialog(self, message="选择蒙版图片", defaultDir=gl.CWD,
                           wildcard=wildcard, style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mask_file = path
            self.mask_text.SetLabelText(f"当前：{os.path.basename(path)}")
            self.current_mask = self.my_wordcloud.load_mask(path)
        
        dlg.Destroy()
    
    def on_process_text(self, event):
        """处理文本"""
        if not self.goal_files:
            wx.MessageBox("请先选择数据文件！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        try:
            lang = 'cn' if self.lang_choice.GetSelection() == 0 else 'en'
            
            if self.stop_word_file:
                self.data_processor.load_stopwords(self.stop_word_file)
            else:
                self.data_processor.load_stopwords(lang=lang)
            
            if self.custom_dict_file:
                self.data_processor.load_custom_dict(self.custom_dict_file)
            
            clean_kwargs = {
                'remove_punct': self.clean_punct.GetValue(),
                'remove_numbers': self.clean_numbers.GetValue(),
                'remove_special_chars': self.clean_special.GetValue(),
            }
            
            all_words = []
            for file_path in self.goal_files:
                text = self.data_processor.import_file(file_path)
                cleaned_text = self.data_processor.clean_text(text, **clean_kwargs)
                words = self.data_processor.segment(cleaned_text, lang=lang)
                all_words.extend(words)
            
            self.word_freq = self.data_processor.get_word_freq(all_words)
            self.processed_text = ' '.join(all_words)
            
            wx.MessageBox(f"文本处理完成！\n共得到 {len(all_words)} 个词汇\n词频统计：{len(self.word_freq)} 个不同词汇", 
                         "处理成功", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"处理失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_generate(self, event):
        """生成词云"""
        if not hasattr(self, 'processed_text') or not self.word_freq:
            wx.MessageBox("请先进行文本处理！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        try:
            font_name = self.font_choice.GetStringSelection()
            font_path = os.path.join(gl.CWD, "data", "font", f"{font_name}.ttf")
            
            bg_color = self.bg_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
            colormap = self.colormaps[self.colormap_choice.GetSelection()]
            
            max_font_size = self.max_font_spin.GetValue()
            if max_font_size == 0:
                max_font_size = None
            
            color_func = None
            if self.use_mask_color.GetValue() and self.current_mask is not None:
                color_func = self.my_wordcloud.get_image_color_func(self.current_mask)
            
            word_freq_dict = dict(self.word_freq)
            
            self.final_pic = self.my_wordcloud.gen_wordcloud(
                seg_list=word_freq_dict,
                font_path=font_path,
                background_color=bg_color,
                margin=self.margin_spin.GetValue(),
                width=self.width_spin.GetValue(),
                height=self.height_spin.GetValue(),
                flag=0,
                mask=self.current_mask,
                colormap=colormap,
                color_func=color_func,
                max_words=self.max_words_spin.GetValue(),
                min_font_size=self.min_font_spin.GetValue(),
                max_font_size=max_font_size,
                prefer_horizontal=self.horiz_spin.GetValue(),
                scale=self.scale_spin.GetValue()
            )
            
            self.update_preview()
            
            wx.MessageBox("词云生成成功！", "成功", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"生成失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_preview(self, event):
        """实时预览"""
        if self.final_pic is None:
            wx.MessageBox("请先生成词云！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        try:
            bg_color = self.bg_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
            colormap = self.colormaps[self.colormap_choice.GetSelection()]
            
            max_font_size = self.max_font_spin.GetValue()
            if max_font_size == 0:
                max_font_size = None
            
            color_func = None
            if self.use_mask_color.GetValue() and self.current_mask is not None:
                color_func = self.my_wordcloud.get_image_color_func(self.current_mask)
            
            self.final_pic = self.my_wordcloud.regenerate_with_params(
                background_color=bg_color,
                margin=self.margin_spin.GetValue(),
                colormap=colormap,
                color_func=color_func,
                min_font_size=self.min_font_spin.GetValue(),
                max_font_size=max_font_size,
                prefer_horizontal=self.horiz_spin.GetValue(),
                scale=self.scale_spin.GetValue()
            )
            
            self.update_preview()
            
        except Exception as e:
            wx.MessageBox(f"预览更新失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def update_preview(self):
        """更新预览显示"""
        if self.final_pic is None:
            return
        
        temp_path = os.path.join(gl.CWD, "data", ".catch", "preview.png")
        self.final_pic.to_file(temp_path)
        
        img = wx.Image(temp_path, wx.BITMAP_TYPE_ANY)
        
        preview_size = (600, 450)
        img = img.Scale(preview_size[0], preview_size[1], wx.IMAGE_QUALITY_HIGH)
        
        self.preview_bitmap.SetBitmap(wx.Bitmap(img))
        self.preview_panel.Layout()
    
    def on_show_freq(self, event):
        """显示词频统计"""
        if not self.word_freq:
            wx.MessageBox("请先进行文本处理！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        try:
            chart_path = os.path.join(gl.CWD, "data", ".catch", "word_freq.png")
            fig = self.visualizer.plot_word_freq_chart(
                self.word_freq, 
                top_n=20,
                title="词频统计TOP20",
                save_path=chart_path
            )
            
            dlg = ChartDialog(self, chart_path, "词频统计")
            dlg.ShowModal()
            dlg.Destroy()
            
        except Exception as e:
            wx.MessageBox(f"显示词频统计失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_export_image(self, event):
        """导出图片"""
        if self.final_pic is None:
            wx.MessageBox("请先生成词云！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        formats = ["png", "jpg", "pdf", "svg"]
        fmt = formats[self.img_format_choice.GetSelection()]
        
        wildcard = f"{fmt.upper()} 文件 (*.{fmt})|*.{fmt}"
        dlg = wx.FileDialog(self, message="保存词云图片", defaultDir=gl.CWD,
                           defaultFile=f"MyWordCloud.{fmt}", wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                self.exporter.export_wordcloud_image(
                    self.final_pic, 
                    path, 
                    format=fmt,
                    dpi=self.dpi_spin.GetValue()
                )
                wx.MessageBox(f"导出成功！\n文件：{path}", "成功", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"导出失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_export_report(self, event):
        """导出报告"""
        if self.final_pic is None or not self.word_freq:
            wx.MessageBox("请先生成词云！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        fmt = "pdf" if self.report_format_choice.GetSelection() == 0 else "md"
        
        wildcard = "PDF报告 (*.pdf)|*.pdf" if fmt == "pdf" else "Markdown报告 (*.md)|*.md"
        dlg = wx.FileDialog(self, message="保存报告", defaultDir=gl.CWD,
                           defaultFile=f"WordCloudReport.{fmt}", wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                wc_image = self.my_wordcloud.to_image()
                
                if fmt == "pdf":
                    self.exporter.generate_pdf_report(
                        self.word_freq,
                        wc_image,
                        None,
                        save_path=path,
                        title="词云分析报告"
                    )
                else:
                    wc_path = os.path.join(gl.CWD, "data", ".catch", "report_wc.png")
                    self.final_pic.to_file(wc_path)
                    
                    report_content = self.exporter.generate_markdown_report(
                        self.word_freq,
                        wc_path,
                        title="词云分析报告"
                    )
                    self.exporter.save_markdown_report(report_content, path)
                
                wx.MessageBox(f"报告生成成功！\n文件：{path}", "成功", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"报告生成失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_export_data(self, event):
        """导出词频数据"""
        if not self.word_freq:
            wx.MessageBox("请先进行文本处理！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        fmt = "csv" if self.data_format_choice.GetSelection() == 0 else "xlsx"
        wildcard = "CSV文件 (*.csv)|*.csv" if fmt == "csv" else "Excel文件 (*.xlsx)|*.xlsx"
        
        dlg = wx.FileDialog(self, message="保存词频数据", defaultDir=gl.CWD,
                           defaultFile=f"WordFrequency.{fmt}", wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                self.exporter.export_data(self.word_freq, path, format=fmt)
                wx.MessageBox(f"数据导出成功！\n文件：{path}", "成功", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"导出失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_batch_export(self, event):
        """批量导出"""
        if len(self.goal_files) < 2:
            wx.MessageBox("请选择多个文件进行批量处理！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        dlg = wx.DirDialog(self, message="选择输出目录", defaultPath=gl.CWD,
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            output_dir = dlg.GetPath()
            try:
                self.batch_process(output_dir)
                wx.MessageBox(f"批量处理完成！\n输出目录：{output_dir}", "成功", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"批量处理失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def batch_process(self, output_dir):
        """批量处理文件"""
        font_name = self.font_choice.GetStringSelection()
        font_path = os.path.join(gl.CWD, "data", "font", f"{font_name}.ttf")
        bg_color = self.bg_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        colormap = self.colormaps[self.colormap_choice.GetSelection()]
        
        lang = 'cn' if self.lang_choice.GetSelection() == 0 else 'en'
        if self.stop_word_file:
            self.data_processor.load_stopwords(self.stop_word_file)
        else:
            self.data_processor.load_stopwords(lang=lang)
        
        clean_kwargs = {
            'remove_punct': self.clean_punct.GetValue(),
            'remove_numbers': self.clean_numbers.GetValue(),
            'remove_special_chars': self.clean_special.GetValue(),
        }
        
        for file_path in self.goal_files:
            try:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                
                text = self.data_processor.import_file(file_path)
                cleaned_text = self.data_processor.clean_text(text, **clean_kwargs)
                words = self.data_processor.segment(cleaned_text, lang=lang)
                word_freq = self.data_processor.get_word_freq(words)
                word_freq_dict = dict(word_freq)
                
                wc = self.my_wordcloud.gen_wordcloud(
                    seg_list=word_freq_dict,
                    font_path=font_path,
                    background_color=bg_color,
                    margin=self.margin_spin.GetValue(),
                    width=self.width_spin.GetValue(),
                    height=self.height_spin.GetValue(),
                    flag=0,
                    mask=self.current_mask,
                    colormap=colormap,
                    max_words=self.max_words_spin.GetValue(),
                    min_font_size=self.min_font_spin.GetValue(),
                    prefer_horizontal=self.horiz_spin.GetValue(),
                    scale=self.scale_spin.GetValue()
                )
                
                save_path = os.path.join(output_dir, f"{filename}_wordcloud.png")
                wc.to_file(save_path)
                
            except Exception as e:
                print(f"处理文件 {file_path} 失败: {str(e)}")
                continue
    
    def update_Choice(self):
        """更新字体选项（被MainFrame调用）"""
        self.update_font_choice()


class ChartDialog(wx.Dialog):
    """图表显示对话框"""
    
    def __init__(self, parent, image_path, title):
        wx.Dialog.__init__(self, parent, title=title, size=(800, 600))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(780, 520, wx.IMAGE_QUALITY_HIGH)
        
        bitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))
        sizer.Add(bitmap, 1, wx.EXPAND | wx.ALL, 10)
        
        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(wx.Button(self, wx.ID_OK))
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(sizer)
