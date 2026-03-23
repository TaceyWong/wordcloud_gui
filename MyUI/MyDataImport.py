# coding:utf-8

import wx
import os
from Utils import gl, data_processor


class MyDataImport(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        
        self.processor = data_processor.DataProcessor(gl.CWD)
        self.imported_files = []
        self.processed_words = []
        self.word_freq = []
        
        self.InitUI()
    
    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        file_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "文件导入"), wx.VERTICAL)
        
        file_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_import_file = wx.Button(file_box.GetStaticBox(), wx.ID_ANY, "导入文件")
        self.btn_import_folder = wx.Button(file_box.GetStaticBox(), wx.ID_ANY, "导入文件夹")
        self.btn_clear = wx.Button(file_box.GetStaticBox(), wx.ID_ANY, "清空列表")
        
        file_btn_sizer.Add(self.btn_import_file, 0, wx.ALL, 5)
        file_btn_sizer.Add(self.btn_import_folder, 0, wx.ALL, 5)
        file_btn_sizer.Add(self.btn_clear, 0, wx.ALL, 5)
        
        file_box.Add(file_btn_sizer, 0, wx.EXPAND, 5)
        
        self.file_list = wx.ListCtrl(file_box.GetStaticBox(), wx.ID_ANY,
                                     style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.file_list.AppendColumn("文件名", width=200)
        self.file_list.AppendColumn("类型", width=80)
        self.file_list.AppendColumn("大小", width=100)
        self.file_list.AppendColumn("状态", width=80)
        
        file_box.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(file_box, 1, wx.EXPAND | wx.ALL, 5)
        
        config_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "数据处理配置"), wx.HORIZONTAL)
        
        left_config = wx.BoxSizer(wx.VERTICAL)
        
        self.chk_remove_punct = wx.CheckBox(config_box.GetStaticBox(), wx.ID_ANY, "去除标点符号")
        self.chk_remove_punct.SetValue(True)
        self.chk_remove_digits = wx.CheckBox(config_box.GetStaticBox(), wx.ID_ANY, "去除数字")
        self.chk_remove_digits.SetValue(True)
        self.chk_remove_special = wx.CheckBox(config_box.GetStaticBox(), wx.ID_ANY, "去除特殊字符")
        self.chk_remove_special.SetValue(True)
        
        left_config.Add(self.chk_remove_punct, 0, wx.ALL, 3)
        left_config.Add(self.chk_remove_digits, 0, wx.ALL, 3)
        left_config.Add(self.chk_remove_special, 0, wx.ALL, 3)
        
        config_box.Add(left_config, 1, wx.EXPAND, 5)
        
        right_config = wx.BoxSizer(wx.VERTICAL)
        
        stopwords_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_stopwords = wx.Button(config_box.GetStaticBox(), wx.ID_ANY, "选择停词表")
        self.lbl_stopwords = wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "当前: 默认停词表")
        stopwords_sizer.Add(self.btn_stopwords, 0, wx.ALL, 3)
        stopwords_sizer.Add(self.lbl_stopwords, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        
        dict_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_dict = wx.Button(config_box.GetStaticBox(), wx.ID_ANY, "自定义词典")
        self.lbl_dict = wx.StaticText(config_box.GetStaticBox(), wx.ID_ANY, "当前: 无")
        dict_sizer.Add(self.btn_dict, 0, wx.ALL, 3)
        dict_sizer.Add(self.lbl_dict, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        
        right_config.Add(stopwords_sizer, 0, wx.EXPAND, 3)
        right_config.Add(dict_sizer, 0, wx.EXPAND, 3)
        
        config_box.Add(right_config, 1, wx.EXPAND, 5)
        
        main_sizer.Add(config_box, 0, wx.EXPAND | wx.ALL, 5)
        
        action_box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "操作"), wx.HORIZONTAL)
        
        self.btn_process = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "处理数据")
        self.btn_view_freq = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "查看词频")
        self.btn_export_words = wx.Button(action_box.GetStaticBox(), wx.ID_ANY, "导出分词结果")
        
        action_box.Add(self.btn_process, 0, wx.ALL, 5)
        action_box.Add(self.btn_view_freq, 0, wx.ALL, 5)
        action_box.Add(self.btn_export_words, 0, wx.ALL, 5)
        
        self.lbl_status = wx.StaticText(action_box.GetStaticBox(), wx.ID_ANY, "就绪")
        action_box.Add(self.lbl_status, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        main_sizer.Add(action_box, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        self.Layout()
        
        self.BindEvents()
    
    def BindEvents(self):
        self.btn_import_file.Bind(wx.EVT_BUTTON, self.OnImportFile)
        self.btn_import_folder.Bind(wx.EVT_BUTTON, self.OnImportFolder)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.OnClear)
        self.btn_stopwords.Bind(wx.EVT_BUTTON, self.OnSelectStopwords)
        self.btn_dict.Bind(wx.EVT_BUTTON, self.OnSelectDict)
        self.btn_process.Bind(wx.EVT_BUTTON, self.OnProcess)
        self.btn_view_freq.Bind(wx.EVT_BUTTON, self.OnViewFreq)
        self.btn_export_words.Bind(wx.EVT_BUTTON, self.OnExportWords)
    
    def OnImportFile(self, event):
        wildcard = "支持的文件|*.txt;*.csv;*.xlsx;*.xls|文本文件 (*.txt)|*.txt|CSV文件 (*.csv)|*.csv|Excel文件 (*.xlsx;*.xls)|*.xlsx;*.xls|所有文件|*.*"
        
        dlg = wx.FileDialog(self, message="选择要导入的文件",
                           defaultDir=gl.CWD,
                           wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                self.AddFileToList(path)
        
        dlg.Destroy()
    
    def OnImportFolder(self, event):
        dlg = wx.DirDialog(self, message="选择包含数据文件的文件夹",
                          defaultPath=gl.CWD,
                          style=wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            folder_path = dlg.GetPath()
            supported_ext = ['.txt', '.csv', '.xlsx', '.xls']
            for filename in os.listdir(folder_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_ext:
                    filepath = os.path.join(folder_path, filename)
                    self.AddFileToList(filepath)
        
        dlg.Destroy()
    
    def AddFileToList(self, filepath):
        if filepath in self.imported_files:
            return
        
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        file_type = {
            '.txt': '文本',
            '.csv': 'CSV',
            '.xlsx': 'Excel',
            '.xls': 'Excel'
        }.get(ext, '未知')
        
        try:
            size = os.path.getsize(filepath)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
        except:
            size_str = "未知"
        
        idx = self.file_list.InsertItem(self.file_list.GetItemCount(), filename)
        self.file_list.SetItem(idx, 1, file_type)
        self.file_list.SetItem(idx, 2, size_str)
        self.file_list.SetItem(idx, 3, "待处理")
        
        self.imported_files.append(filepath)
    
    def OnClear(self, event):
        self.file_list.DeleteAllItems()
        self.imported_files = []
        self.processed_words = []
        self.word_freq = []
        self.lbl_status.SetLabel("已清空")
    
    def OnSelectStopwords(self, event):
        wildcard = "文本文件 (*.txt)|*.txt"
        dlg = wx.FileDialog(self, message="选择停词表文件",
                           defaultDir=gl.get_data_path('stopwords'),
                           wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            count = self.processor.load_stopwords(path)
            self.lbl_stopwords.SetLabel(f"当前: {os.path.basename(path)} ({count}词)")
        
        dlg.Destroy()
    
    def OnSelectDict(self, event):
        wildcard = "文本文件 (*.txt)|*.txt"
        dlg = wx.FileDialog(self, message="选择自定义词典文件",
                           defaultDir=gl.CWD,
                           wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.processor.load_custom_dict(path)
            self.lbl_dict.SetLabel(f"当前: {os.path.basename(path)}")
        
        dlg.Destroy()
    
    def OnProcess(self, event):
        if not self.imported_files:
            dlg = wx.MessageDialog(self, "请先导入文件！", "提示",
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        clean_options = {
            'remove_punctuation': self.chk_remove_punct.GetValue(),
            'remove_digits': self.chk_remove_digits.GetValue(),
            'remove_special_chars': self.chk_remove_special.GetValue(),
            'remove_whitespace': True
        }
        
        self.processed_words = []
        
        progress_dialog = wx.ProgressDialog("处理中", "正在处理文件...",
                                           maximum=len(self.imported_files),
                                           parent=self,
                                           style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
        
        for i, filepath in enumerate(self.imported_files):
            progress_dialog.Update(i + 1, f"处理: {os.path.basename(filepath)}")
            
            try:
                words = self.processor.process_file(filepath, clean_options=clean_options)
                self.processed_words.extend(words)
                self.file_list.SetItem(i, 3, "已完成")
            except Exception as e:
                self.file_list.SetItem(i, 3, f"错误: {str(e)[:20]}")
        
        progress_dialog.Destroy()
        
        self.word_freq = self.processor.get_word_frequency(self.processed_words)
        
        total_words = len(self.processed_words)
        unique_words = len(self.word_freq)
        self.lbl_status.SetLabel(f"完成: 共{total_words}词, {unique_words}个不同词")
        
        dlg = wx.MessageDialog(self, f"处理完成！\n总词数: {total_words}\n不同词数: {unique_words}",
                               "处理结果", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnViewFreq(self, event):
        if not self.word_freq:
            dlg = wx.MessageDialog(self, "请先处理数据！", "提示",
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        freq_dialog = FrequencyDialog(self, self.word_freq[:50])
        freq_dialog.ShowModal()
        freq_dialog.Destroy()
    
    def OnExportWords(self, event):
        if not self.processed_words:
            dlg = wx.MessageDialog(self, "请先处理数据！", "提示",
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        wildcard = "文本文件 (*.txt)|*.txt|CSV文件 (*.csv)|*.csv"
        dlg = wx.FileDialog(self, message="保存分词结果",
                           defaultDir=gl.CWD,
                           defaultFile="words_result",
                           wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            ext = os.path.splitext(path)[1].lower()
            
            try:
                if ext == '.csv':
                    import csv
                    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['词语', '频次'])
                        for word, freq in self.word_freq:
                            writer.writerow([word, freq])
                else:
                    with open(path, 'w', encoding='utf-8') as f:
                        for word, freq in self.word_freq:
                            f.write(f"{word}: {freq}\n")
                
                dlg2 = wx.MessageDialog(self, f"导出成功！\n保存至: {path}",
                                       "导出完成", wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
            except Exception as e:
                dlg2 = wx.MessageDialog(self, f"导出失败: {str(e)}",
                                       "错误", wx.OK | wx.ICON_ERROR)
                dlg2.ShowModal()
                dlg2.Destroy()
        
        dlg.Destroy()
    
    def update_Choice(self):
        pass
    
    def refresh_data(self):
        pass


class FrequencyDialog(wx.Dialog):
    
    def __init__(self, parent, word_freq):
        wx.Dialog.__init__(self, parent, title="词频统计", size=(500, 400))
        
        self.word_freq = word_freq
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.list_ctrl = wx.ListCtrl(panel, wx.ID_ANY, style=wx.LC_REPORT)
        self.list_ctrl.AppendColumn("排名", width=60)
        self.list_ctrl.AppendColumn("词语", width=200)
        self.list_ctrl.AppendColumn("频次", width=100)
        self.list_ctrl.AppendColumn("占比", width=100)
        
        total = sum(freq for _, freq in word_freq) if word_freq else 1
        
        for i, (word, freq) in enumerate(word_freq, 1):
            idx = self.list_ctrl.InsertItem(i - 1, str(i))
            self.list_ctrl.SetItem(idx, 1, word)
            self.list_ctrl.SetItem(idx, 2, str(freq))
            self.list_ctrl.SetItem(idx, 3, f"{freq / total * 100:.2f}%")
        
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        btn_close = wx.Button(panel, wx.ID_CLOSE, "关闭")
        sizer.Add(btn_close, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        self.Bind(wx.EVT_BUTTON, lambda e: self.Close(), btn_close)
