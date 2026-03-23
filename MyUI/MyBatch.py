# coding:utf-8

import wx
import os
import threading
from Utils import gl, new_wordcloud, exporter


class MyBatch(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        
        self.files_to_process = []
        self.output_dir = None
        self.processing = False
        
        self.InitUI()
    
    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        source_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "源文件"), wx.VERTICAL)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_add_files = wx.Button(source_box.GetStaticBox(), wx.ID_ANY, "添加文件")
        self.btn_add_folder = wx.Button(source_box.GetStaticBox(), wx.ID_ANY, "添加文件夹")
        self.btn_remove = wx.Button(source_box.GetStaticBox(), wx.ID_ANY, "移除选中")
        self.btn_clear = wx.Button(source_box.GetStaticBox(), wx.ID_ANY, "清空列表")
        btn_sizer.Add(self.btn_add_files, 0, wx.ALL, 3)
        btn_sizer.Add(self.btn_add_folder, 0, wx.ALL, 3)
        btn_sizer.Add(self.btn_remove, 0, wx.ALL, 3)
        btn_sizer.Add(self.btn_clear, 0, wx.ALL, 3)
        
        source_box.Add(btn_sizer, 0, wx.EXPAND, 5)
        
        self.file_list = wx.ListCtrl(source_box.GetStaticBox(), wx.ID_ANY,
                                     style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.file_list.AppendColumn("文件名", width=200)
        self.file_list.AppendColumn("路径", width=300)
        self.file_list.AppendColumn("状态", width=80)
        
        source_box.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(source_box, 1, wx.EXPAND | wx.ALL, 5)
        
        config_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "配置"), wx.HORIZONTAL)
        
        left_config = wx.BoxSizer(wx.VERTICAL)
        
        font_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_sizer.Add(wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "字体:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.choice_font = wx.Choice(config_box.GetStaticBox(), wx.ID_ANY, choices=[])
        self.update_font_choice()
        font_sizer.Add(self.choice_font, 1, wx.ALL, 3)
        left_config.Add(font_sizer, 0, wx.EXPAND, 5)
        
        size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        size_sizer.Add(wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "宽度:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.spin_width = wx.SpinCtrl(config_box.GetStaticBox(), wx.ID_ANY, value="800", min=200, max=4000)
        size_sizer.Add(self.spin_width, 1, wx.ALL, 3)
        size_sizer.Add(wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "高度:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.spin_height = wx.SpinCtrl(config_box.GetStaticBox(), wx.ID_ANY, value="600", min=200, max=4000)
        size_sizer.Add(self.spin_height, 1, wx.ALL, 3)
        left_config.Add(size_sizer, 0, wx.EXPAND, 5)
        
        config_box.Add(left_config, 1, wx.EXPAND, 5)
        
        right_config = wx.BoxSizer(wx.VERTICAL)
        
        bg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bg_sizer.Add(wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "背景色:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.color_picker_bg = wx.ColourPickerCtrl(config_box.GetStaticBox(), wx.ID_ANY, wx.WHITE)
        bg_sizer.Add(self.color_picker_bg, 0, wx.ALL, 3)
        right_config.Add(bg_sizer, 0, wx.EXPAND, 5)
        
        format_sizer = wx.BoxSizer(wx.HORIZONTAL)
        format_sizer.Add(wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "输出格式:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.choice_format = wx.Choice(config_box.GetStaticBox(), wx.ID_ANY, 
                                       choices=["PNG", "JPG", "SVG", "PDF"])
        self.choice_format.SetSelection(0)
        format_sizer.Add(self.choice_format, 1, wx.ALL, 3)
        right_config.Add(format_sizer, 0, wx.EXPAND, 5)
        
        config_box.Add(right_config, 1, wx.EXPAND, 5)
        
        main_sizer.Add(config_box, 0, wx.EXPAND | wx.ALL, 5)
        
        output_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "输出设置"), wx.HORIZONTAL)
        
        self.btn_output_dir = wx.Button(output_box.GetStaticBox(), wx.ID_ANY, "选择输出目录")
        self.lbl_output_dir = wx.StaticText(output_box.GetStaticBox(), wx.ID_ANY, "当前: 未选择")
        
        output_box.Add(self.btn_output_dir, 0, wx.ALL, 5)
        output_box.Add(self.lbl_output_dir, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        main_sizer.Add(output_box, 0, wx.EXPAND | wx.ALL, 5)
        
        action_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "操作"), wx.HORIZONTAL)
        
        self.btn_start = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "开始批量处理")
        self.btn_stop = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "停止")
        self.btn_stop.Disable()
        
        self.gauge = wx.Gauge(action_box.GetStaticBox(), wx.ID_ANY, range=100)
        
        self.lbl_status = wx.StaticText(action_box.GetStaticBox(), wx.ID_ANY, "就绪")
        
        action_box.Add(self.btn_start, 0, wx.ALL, 5)
        action_box.Add(self.btn_stop, 0, wx.ALL, 5)
        action_box.Add(self.gauge, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        action_box.Add(self.lbl_status, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        main_sizer.Add(action_box, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        self.Layout()
        
        self.BindEvents()
    
    def BindEvents(self):
        self.btn_add_files.Bind(wx.EVT_BUTTON, self.OnAddFiles)
        self.btn_add_folder.Bind(wx.EVT_BUTTON, self.OnAddFolder)
        self.btn_remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.OnClear)
        self.btn_output_dir.Bind(wx.EVT_BUTTON, self.OnSelectOutputDir)
        self.btn_start.Bind(wx.EVT_BUTTON, self.OnStart)
        self.btn_stop.Bind(wx.EVT_BUTTON, self.OnStop)
    
    def update_font_choice(self):
        fonts = gl.get_available_fonts()
        self.choice_font.Clear()
        if fonts:
            self.choice_font.AppendItems(fonts)
            self.choice_font.SetSelection(0)
    
    def update_Choice(self):
        self.update_font_choice()
    
    def OnAddFiles(self, event):
        wildcard = "文本文件 (*.txt)|*.txt|CSV文件 (*.csv)|*.csv|所有文件|*.*"
        dlg = wx.FileDialog(self, message="选择文件",
                           defaultDir=gl.CWD,
                           wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                self.AddFileToList(path)
        
        dlg.Destroy()
    
    def OnAddFolder(self, event):
        dlg = wx.DirDialog(self, message="选择文件夹",
                          defaultPath=gl.CWD,
                          style=wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            folder_path = dlg.GetPath()
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt') or filename.endswith('.csv'):
                    filepath = os.path.join(folder_path, filename)
                    self.AddFileToList(filepath)
        
        dlg.Destroy()
    
    def AddFileToList(self, filepath):
        for item in self.files_to_process:
            if item['path'] == filepath:
                return
        
        filename = os.path.basename(filepath)
        idx = self.file_list.InsertItem(self.file_list.GetItemCount(), filename)
        self.file_list.SetItem(idx, 1, filepath)
        self.file_list.SetItem(idx, 2, "待处理")
        
        self.files_to_process.append({
            'path': filepath,
            'filename': filename,
            'status': 'pending'
        })
    
    def OnRemove(self, event):
        idx = self.file_list.GetFirstSelected()
        if idx >= 0:
            self.file_list.DeleteItem(idx)
            self.files_to_process.pop(idx)
    
    def OnClear(self, event):
        self.file_list.DeleteAllItems()
        self.files_to_process = []
    
    def OnSelectOutputDir(self, event):
        dlg = wx.DirDialog(self, message="选择输出目录",
                          defaultPath=gl.CWD,
                          style=wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.output_dir = dlg.GetPath()
            self.lbl_output_dir.SetLabel(f"当前: {self.output_dir}")
        
        dlg.Destroy()
    
    def OnStart(self, event):
        if not self.files_to_process:
            self.show_warning("请先添加要处理的文件")
            return
        
        if not self.output_dir:
            self.show_warning("请先选择输出目录")
            return
        
        self.processing = True
        self.btn_start.Disable()
        self.btn_stop.Enable()
        
        self.gauge.SetRange(len(self.files_to_process))
        self.gauge.SetValue(0)
        
        thread = threading.Thread(target=self.ProcessFiles)
        thread.daemon = True
        thread.start()
    
    def ProcessFiles(self):
        font_name = self.choice_font.GetStringSelection()
        font_path = gl.get_font_path(font_name) if font_name else None
        width = self.spin_width.GetValue()
        height = self.spin_height.GetValue()
        bg_color = self.color_picker_bg.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        output_format = self.choice_format.GetStringSelection().lower()
        
        wc = new_wordcloud.MyWordCloud()
        stopwords_path = gl.get_stopwords_path('cn')
        if os.path.exists(stopwords_path):
            wc.load_stopwords(stopwords_path)
        
        exporter_inst = exporter.WordCloudExporter()
        
        for i, file_info in enumerate(self.files_to_process):
            if not self.processing:
                break
            
            wx.CallAfter(self.UpdateProgress, i, f"处理: {file_info['filename']}")
            
            try:
                words = wc.cut_file(file_info['path'])
                word_freq = wc.get_word_frequency()
                
                wordcloud = wc.generate_wordcloud(
                    word_freq=word_freq,
                    font_path=font_path,
                    width=width,
                    height=height,
                    background_color=bg_color
                )
                
                base_name = os.path.splitext(file_info['filename'])[0]
                output_path = os.path.join(self.output_dir, f"{base_name}.{output_format}")
                
                exporter_inst.export_image(wordcloud, output_path, dpi=300)
                
                wx.CallAfter(self.UpdateFileStatus, i, "完成")
                
            except Exception as e:
                wx.CallAfter(self.UpdateFileStatus, i, f"错误: {str(e)[:10]}")
        
        wx.CallAfter(self.ProcessComplete)
    
    def UpdateProgress(self, value, status):
        self.gauge.SetValue(value)
        self.lbl_status.SetLabel(status)
    
    def UpdateFileStatus(self, idx, status):
        self.file_list.SetItem(idx, 2, status)
    
    def ProcessComplete(self):
        self.processing = False
        self.btn_start.Enable()
        self.btn_stop.Disable()
        self.gauge.SetValue(self.gauge.GetRange())
        self.lbl_status.SetLabel("处理完成")
        
        dlg = wx.MessageDialog(self, "批量处理完成！", "完成",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnStop(self, event):
        self.processing = False
        self.lbl_status.SetLabel("已停止")
    
    def show_warning(self, msg):
        dlg = wx.MessageDialog(self, msg, "警告", wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
    
    def refresh_data(self):
        pass
