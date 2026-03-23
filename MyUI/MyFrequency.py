# coding:utf-8

import wx
import os
import io
from Utils import gl, visualizer, new_wordcloud, exporter


class MyFrequency(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        
        self.visualizer = visualizer.FrequencyVisualizer()
        self.word_freq = []
        self.current_chart = None
        self.wordcloud = None
        
        self.InitUI()
    
    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        left_panel = wx.Panel(self)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_box = wx.StaticBoxSizer(wx.StaticBox(left_panel, wx.ID_ANY, "数据输入"), wx.VERTICAL)
        
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_load_freq = wx.Button(input_box.GetStaticBox(), wx.ID_ANY, "加载词频文件")
        self.btn_load_text = wx.Button(input_box.GetStaticBox(), wx.ID_ANY, "加载文本文件")
        self.btn_paste = wx.Button(input_box.GetStaticBox(), wx.ID_ANY, "粘贴文本")
        file_sizer.Add(self.btn_load_freq, 0, wx.ALL, 3)
        file_sizer.Add(self.btn_load_text, 0, wx.ALL, 3)
        file_sizer.Add(self.btn_paste, 0, wx.ALL, 3)
        
        input_box.Add(file_sizer, 0, wx.EXPAND, 5)
        
        self.lbl_data_status = wx.StaticText(input_box.GetStaticBox(), wx.ID_ANY, "当前: 无数据")
        input_box.Add(self.lbl_data_status, 0, wx.ALL, 5)
        
        left_sizer.Add(input_box, 0, wx.EXPAND | wx.ALL, 5)
        
        chart_box = wx.StaticBoxSizer(wx.StaticBox(left_panel, wx.ID_ANY, "图表设置"), wx.VERTICAL)
        
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_sizer.Add(wx.StaticText(chart_box.GetStaticBox(), wx.ID_ANY, "图表类型:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.choice_chart_type = wx.Choice(chart_box.GetStaticBox(), wx.ID_ANY, choices=["柱状图", "横向柱状图", "饼图"])
        self.choice_chart_type.SetSelection(0)
        type_sizer.Add(self.choice_chart_type, 1, wx.ALL, 3)
        chart_box.Add(type_sizer, 0, wx.EXPAND, 5)
        
        topn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        topn_sizer.Add(wx.StaticText(chart_box.GetStaticBox(), wx.ID_ANY, "显示数量:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.spin_topn = wx.SpinCtrl(chart_box.GetStaticBox(), wx.ID_ANY, value="20", min=5, max=100)
        topn_sizer.Add(self.spin_topn, 1, wx.ALL, 3)
        chart_box.Add(topn_sizer, 0, wx.EXPAND, 5)
        
        color_sizer = wx.BoxSizer(wx.HORIZONTAL)
        color_sizer.Add(wx.StaticText(chart_box.GetStaticBox(), wx.ID_ANY, "颜色方案:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.choice_colormap = wx.Choice(chart_box.GetStaticBox(), wx.ID_ANY, 
                                         choices=['viridis', 'plasma', 'Blues', 'Greens', 'Oranges', 'Reds'])
        self.choice_colormap.SetSelection(0)
        color_sizer.Add(self.choice_colormap, 1, wx.ALL, 3)
        chart_box.Add(color_sizer, 0, wx.EXPAND, 5)
        
        left_sizer.Add(chart_box, 0, wx.EXPAND | wx.ALL, 5)
        
        wordcloud_box = wx.StaticBoxSizer(wx.StaticBox(left_panel, wx.ID_ANY, "词云设置"), wx.VERTICAL)
        
        font_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_sizer.Add(wx.StaticText(wordcloud_box.GetStaticBox(), wx.ID_ANY, "字体:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.choice_font = wx.Choice(wordcloud_box.GetStaticBox(), wx.ID_ANY, choices=[])
        self.update_font_choice()
        font_sizer.Add(self.choice_font, 1, wx.ALL, 3)
        wordcloud_box.Add(font_sizer, 0, wx.EXPAND, 5)
        
        size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        size_sizer.Add(wx.StaticText(wordcloud_box.GetStaticBox(), wx.ID_ANY, "宽度:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.spin_width = wx.SpinCtrl(wordcloud_box.GetStaticBox(), wx.ID_ANY, value="800", min=200, max=4000)
        size_sizer.Add(self.spin_width, 1, wx.ALL, 3)
        size_sizer.Add(wx.StaticText(wordcloud_box.GetStaticBox(), wx.ID_ANY, "高度:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.spin_height = wx.SpinCtrl(wordcloud_box.GetStaticBox(), wx.ID_ANY, value="600", min=200, max=4000)
        size_sizer.Add(self.spin_height, 1, wx.ALL, 3)
        wordcloud_box.Add(size_sizer, 0, wx.EXPAND, 5)
        
        bg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bg_sizer.Add(wx.StaticText(wordcloud_box.GetStaticBox(), wx.ID_ANY, "背景色:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.color_picker_bg = wx.ColourPickerCtrl(wordcloud_box.GetStaticBox(), wx.ID_ANY, wx.WHITE)
        bg_sizer.Add(self.color_picker_bg, 0, wx.ALL, 3)
        wordcloud_box.Add(bg_sizer, 0, wx.EXPAND, 5)
        
        left_sizer.Add(wordcloud_box, 0, wx.EXPAND | wx.ALL, 5)
        
        action_box = wx.StaticBoxSizer(wx.StaticBox(left_panel, wx.ID_ANY, "操作"), wx.VERTICAL)
        
        self.btn_generate_chart = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "生成图表")
        self.btn_generate_wordcloud = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "生成词云")
        self.btn_export_chart = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "导出图表")
        self.btn_export_wordcloud = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "导出词云")
        self.btn_export_report = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "生成报告")
        
        action_box.Add(self.btn_generate_chart, 0, wx.EXPAND | wx.ALL, 3)
        action_box.Add(self.btn_generate_wordcloud, 0, wx.EXPAND | wx.ALL, 3)
        action_box.Add(self.btn_export_chart, 0, wx.EXPAND | wx.ALL, 3)
        action_box.Add(self.btn_export_wordcloud, 0, wx.EXPAND | wx.ALL, 3)
        action_box.Add(self.btn_export_report, 0, wx.EXPAND | wx.ALL, 3)
        
        left_sizer.Add(action_box, 0, wx.EXPAND | wx.ALL, 5)
        
        left_panel.SetSizer(left_sizer)
        main_sizer.Add(left_panel, 0, wx.EXPAND, 0)
        
        right_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "预览"), wx.VERTICAL)
        
        self.notebook = wx.Notebook(right_box.GetStaticBox(), wx.ID_ANY)
        
        self.panel_chart = wx.Panel(self.notebook)
        chart_sizer = wx.BoxSizer(wx.VERTICAL)
        self.bitmap_chart = wx.StaticBitmap(self.panel_chart, wx.ID_ANY, wx.Bitmap(600, 400))
        chart_sizer.Add(self.bitmap_chart, 1, wx.EXPAND | wx.ALL, 5)
        self.panel_chart.SetSizer(chart_sizer)
        
        self.panel_wordcloud = wx.Panel(self.notebook)
        wc_sizer = wx.BoxSizer(wx.VERTICAL)
        self.bitmap_wordcloud = wx.StaticBitmap(self.panel_wordcloud, wx.ID_ANY, wx.Bitmap(600, 400))
        wc_sizer.Add(self.bitmap_wordcloud, 1, wx.EXPAND | wx.ALL, 5)
        self.panel_wordcloud.SetSizer(wc_sizer)
        
        self.notebook.AddPage(self.panel_chart, "词频图表")
        self.notebook.AddPage(self.panel_wordcloud, "词云图")
        
        right_box.Add(self.notebook, 1, wx.EXPAND, 5)
        
        main_sizer.Add(right_box, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        self.Layout()
        
        self.BindEvents()
    
    def BindEvents(self):
        self.btn_load_freq.Bind(wx.EVT_BUTTON, self.OnLoadFreq)
        self.btn_load_text.Bind(wx.EVT_BUTTON, self.OnLoadText)
        self.btn_paste.Bind(wx.EVT_BUTTON, self.OnPasteText)
        self.btn_generate_chart.Bind(wx.EVT_BUTTON, self.OnGenerateChart)
        self.btn_generate_wordcloud.Bind(wx.EVT_BUTTON, self.OnGenerateWordcloud)
        self.btn_export_chart.Bind(wx.EVT_BUTTON, self.OnExportChart)
        self.btn_export_wordcloud.Bind(wx.EVT_BUTTON, self.OnExportWordcloud)
        self.btn_export_report.Bind(wx.EVT_BUTTON, self.OnExportReport)
    
    def update_font_choice(self):
        fonts = gl.get_available_fonts()
        self.choice_font.Clear()
        if fonts:
            self.choice_font.AppendItems(fonts)
            self.choice_font.SetSelection(0)
    
    def update_Choice(self):
        self.update_font_choice()
    
    def OnLoadFreq(self, event):
        wildcard = "词频文件 (*.txt;*.csv)|*.txt;*.csv"
        dlg = wx.FileDialog(self, message="加载词频文件",
                           defaultDir=gl.CWD,
                           wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                self.word_freq = self.load_freq_file(path)
                self.lbl_data_status.SetLabel(f"已加载: {os.path.basename(path)} ({len(self.word_freq)}词)")
            except Exception as e:
                self.show_error(f"加载失败: {str(e)}")
        
        dlg.Destroy()
    
    def load_freq_file(self, filepath):
        freq_list = []
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.csv':
            import csv
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        freq_list.append((row[0], int(row[1])))
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        freq_list.append((parts[0].strip(), int(parts[1].strip())))
        
        return freq_list
    
    def OnLoadText(self, event):
        wildcard = "文本文件 (*.txt)|*.txt"
        dlg = wx.FileDialog(self, message="加载文本文件",
                           defaultDir=gl.CWD,
                           wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                wc = new_wordcloud.MyWordCloud()
                stopwords_path = gl.get_stopwords_path('cn')
                if os.path.exists(stopwords_path):
                    wc.load_stopwords(stopwords_path)
                
                words = wc.cut_file(path)
                self.word_freq = wc.get_word_frequency()
                
                self.lbl_data_status.SetLabel(f"已加载: {os.path.basename(path)} ({len(self.word_freq)}词)")
            except Exception as e:
                self.show_error(f"加载失败: {str(e)}")
        
        dlg.Destroy()
    
    def OnPasteText(self, event):
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                data = wx.TextDataObject()
                wx.TheClipboard.GetData(data)
                text = data.GetText()
                wx.TheClipboard.Close()
                
                wc = new_wordcloud.MyWordCloud()
                stopwords_path = gl.get_stopwords_path('cn')
                if os.path.exists(stopwords_path):
                    wc.load_stopwords(stopwords_path)
                
                words = wc.cut_text(text)
                self.word_freq = wc.get_word_frequency()
                
                self.lbl_data_status.SetLabel(f"已处理粘贴文本 ({len(self.word_freq)}词)")
            else:
                wx.TheClipboard.Close()
                self.show_error("剪贴板中没有文本数据")
    
    def OnGenerateChart(self, event):
        if not self.word_freq:
            self.show_warning("请先加载数据")
            return
        
        top_n = self.spin_topn.GetValue()
        chart_type = self.choice_chart_type.GetSelection()
        colormap = self.choice_colormap.GetStringSelection()
        
        try:
            if chart_type == 0:
                self.current_chart = self.visualizer.create_bar_chart(
                    self.word_freq, top_n=top_n, color=self.get_color_from_colormap(colormap))
            elif chart_type == 1:
                self.current_chart = self.visualizer.create_horizontal_bar_chart(
                    self.word_freq, top_n=top_n, color=self.get_color_from_colormap(colormap))
            else:
                self.current_chart = self.visualizer.create_pie_chart(
                    self.word_freq, top_n=top_n)
            
            buf = io.BytesIO()
            self.current_chart.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            img = wx.Image(buf, wx.BITMAP_TYPE_PNG)
            self.bitmap_chart.SetBitmap(wx.Bitmap(img))
            
            import matplotlib.pyplot as plt
            plt.close(self.current_chart)
            
        except Exception as e:
            self.show_error(f"生成图表失败: {str(e)}")
    
    def get_color_from_colormap(self, colormap):
        colors = {
            'viridis': '#440154',
            'plasma': '#0d0887',
            'Blues': '#3182bd',
            'Greens': '#31a354',
            'Oranges': '#e6550d',
            'Reds': '#de2d26'
        }
        return colors.get(colormap, '#3498db')
    
    def OnGenerateWordcloud(self, event):
        if not self.word_freq:
            self.show_warning("请先加载数据")
            return
        
        font_name = self.choice_font.GetStringSelection()
        font_path = gl.get_font_path(font_name) if font_name else None
        width = self.spin_width.GetValue()
        height = self.spin_height.GetValue()
        bg_color = self.color_picker_bg.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        colormap = self.choice_colormap.GetStringSelection()
        
        try:
            wc = new_wordcloud.MyWordCloud()
            self.wordcloud = wc.generate_wordcloud(
                word_freq=self.word_freq,
                font_path=font_path,
                width=width,
                height=height,
                background_color=bg_color,
                colormap=colormap
            )
            
            buf = io.BytesIO()
            self.wordcloud.to_image().save(buf, format='PNG')
            buf.seek(0)
            
            img = wx.Image(buf, wx.BITMAP_TYPE_PNG)
            self.bitmap_wordcloud.SetBitmap(wx.Bitmap(img))
            
        except Exception as e:
            self.show_error(f"生成词云失败: {str(e)}")
    
    def OnExportChart(self, event):
        if self.current_chart is None:
            self.show_warning("请先生成图表")
            return
        
        wildcard = "PNG图片 (*.png)|*.png|JPG图片 (*.jpg)|*.jpg|PDF文件 (*.pdf)|*.pdf|SVG文件 (*.svg)|*.svg"
        dlg = wx.FileDialog(self, message="导出图表",
                           defaultDir=gl.CWD,
                           defaultFile="frequency_chart",
                           wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                self.current_chart.savefig(path, dpi=300, bbox_inches='tight')
                self.show_info(f"导出成功: {path}")
            except Exception as e:
                self.show_error(f"导出失败: {str(e)}")
        
        dlg.Destroy()
    
    def OnExportWordcloud(self, event):
        if self.wordcloud is None:
            self.show_warning("请先生成词云")
            return
        
        wildcard = "PNG图片 (*.png)|*.png|JPG图片 (*.jpg)|*.jpg|PDF文件 (*.pdf)|*.pdf|SVG文件 (*.svg)|*.svg"
        dlg = wx.FileDialog(self, message="导出词云",
                           defaultDir=gl.CWD,
                           defaultFile="wordcloud",
                           wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                exporter_inst = exporter.WordCloudExporter()
                exporter_inst.export_image(self.wordcloud, path, dpi=300)
                self.show_info(f"导出成功: {path}")
            except Exception as e:
                self.show_error(f"导出失败: {str(e)}")
        
        dlg.Destroy()
    
    def OnExportReport(self, event):
        if not self.word_freq:
            self.show_warning("请先加载数据")
            return
        
        wildcard = "Markdown文件 (*.md)|*.md|HTML文件 (*.html)|*.html"
        dlg = wx.FileDialog(self, message="导出报告",
                           defaultDir=gl.CWD,
                           defaultFile="wordcloud_report",
                           wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            ext = os.path.splitext(path)[1].lower()
            
            try:
                report_gen = exporter.ReportGenerator(gl.CWD)
                
                if ext == '.html':
                    report_gen.generate_html_report(self.word_freq, output_path=path, title='词云分析报告')
                else:
                    report_gen.generate_markdown_report(self.word_freq, output_path=path, title='词云分析报告')
                
                self.show_info(f"报告已生成: {path}")
            except Exception as e:
                self.show_error(f"生成报告失败: {str(e)}")
        
        dlg.Destroy()
    
    def show_info(self, msg):
        dlg = wx.MessageDialog(self, msg, "提示", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def show_warning(self, msg):
        dlg = wx.MessageDialog(self, msg, "警告", wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
    
    def show_error(self, msg):
        dlg = wx.MessageDialog(self, msg, "错误", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    
    def refresh_data(self):
        pass
