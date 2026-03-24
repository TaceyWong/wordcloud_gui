# coding:utf-8
"""
数据导入页面 - 支持Excel/CSV/TXT文件导入
"""

from __future__ import print_function, unicode_literals
import wx
import os
import sys

from Utils import gl
from Utils.data_processor import DataProcessor

# Python 2/3 兼容性
if sys.version_info[0] == 2:
    import cStringIO
else:
    from io import BytesIO as cStringIO


class MyDataImport(wx.Panel):
    """数据导入页面"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))

        # 初始化数据处理器
        self.data_processor = DataProcessor()
        self.imported_files = []
        self.text_content = ""

        self.init_ui()
        self.bind_events()

    def init_ui(self):
        """初始化界面"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 文件选择区域
        file_box = wx.StaticBox(self, wx.ID_ANY, u"文件导入")
        file_sizer = wx.StaticBoxSizer(file_box, wx.VERTICAL)

        # 文件类型选择
        type_sizer = wx.FlexGridSizer(0, 2, 5, 10)
        type_sizer.AddGrowableCol(1)

        type_label = wx.StaticText(file_box, wx.ID_ANY, u"文件类型:")
        self.file_type_choice = wx.Choice(file_box, wx.ID_ANY, choices=[
            u"自动识别", u"TXT文本", u"CSV表格", u"Excel表格"
        ])
        self.file_type_choice.SetSelection(0)

        type_sizer.Add(type_label, 0, wx.ALIGN_CENTER_VERTICAL)
        type_sizer.Add(self.file_type_choice, 1, wx.EXPAND)

        # 文本列选择（针对表格文件）
        col_label = wx.StaticText(file_box, wx.ID_ANY, u"文本列名/索引:")
        self.col_text = wx.TextCtrl(file_box, wx.ID_ANY, u"",
                                    style=wx.TE_PROCESS_ENTER)
        self.col_text.SetToolTip(u"对于CSV/Excel文件，指定包含文本的列名或索引（从0开始）")

        type_sizer.Add(col_label, 0, wx.ALIGN_CENTER_VERTICAL)
        type_sizer.Add(self.col_text, 1, wx.EXPAND)

        file_sizer.Add(type_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 文件列表
        list_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.file_list = wx.ListBox(file_box, wx.ID_ANY, style=wx.LB_EXTENDED)
        self.file_list.SetMinSize((300, 150))

        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        self.add_btn = wx.Button(file_box, wx.ID_ANY, u"添加文件")
        self.remove_btn = wx.Button(file_box, wx.ID_ANY, u"移除选中")
        self.clear_btn = wx.Button(file_box, wx.ID_ANY, u"清空列表")

        btn_sizer.Add(self.add_btn, 0, wx.EXPAND | wx.ALL, 2)
        btn_sizer.Add(self.remove_btn, 0, wx.EXPAND | wx.ALL, 2)
        btn_sizer.Add(self.clear_btn, 0, wx.EXPAND | wx.ALL, 2)

        list_sizer.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 5)
        list_sizer.Add(btn_sizer, 0, wx.ALL, 5)

        file_sizer.Add(list_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # 导入按钮
        self.import_btn = wx.Button(file_box, wx.ID_ANY, u"开始导入")
        self.import_btn.SetBackgroundColour(wx.Colour(0, 120, 215))
        self.import_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        file_sizer.Add(self.import_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        main_sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # 文本清洗配置区域
        clean_box = wx.StaticBox(self, wx.ID_ANY, u"文本清洗配置")
        clean_sizer = wx.StaticBoxSizer(clean_box, wx.VERTICAL)

        # 清洗选项
        self.remove_punct_chk = wx.CheckBox(clean_box, wx.ID_ANY, u"去除标点符号")
        self.remove_punct_chk.SetValue(True)
        self.remove_num_chk = wx.CheckBox(clean_box, wx.ID_ANY, u"去除数字")
        self.remove_num_chk.SetValue(True)
        self.remove_space_chk = wx.CheckBox(clean_box, wx.ID_ANY, u"去除多余空格")
        self.remove_space_chk.SetValue(True)
        self.remove_eng_chk = wx.CheckBox(clean_box, wx.ID_ANY, u"去除英文")
        self.lowercase_chk = wx.CheckBox(clean_box, wx.ID_ANY, u"转为小写")
        self.lowercase_chk.SetValue(True)

        chk_sizer = wx.FlexGridSizer(0, 3, 5, 10)
        chk_sizer.Add(self.remove_punct_chk, 0, wx.ALL, 5)
        chk_sizer.Add(self.remove_num_chk, 0, wx.ALL, 5)
        chk_sizer.Add(self.remove_space_chk, 0, wx.ALL, 5)
        chk_sizer.Add(self.remove_eng_chk, 0, wx.ALL, 5)
        chk_sizer.Add(self.lowercase_chk, 0, wx.ALL, 5)

        clean_sizer.Add(chk_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 停用词配置
        stop_sizer = wx.FlexGridSizer(0, 3, 5, 10)
        stop_sizer.AddGrowableCol(1)

        stop_label = wx.StaticText(clean_box, wx.ID_ANY, u"停用词表:")
        self.stopword_text = wx.TextCtrl(clean_box, wx.ID_ANY, u"",
                                         style=wx.TE_READONLY)
        self.stopword_btn = wx.Button(clean_box, wx.ID_ANY, u"选择文件")

        stop_sizer.Add(stop_label, 0, wx.ALIGN_CENTER_VERTICAL)
        stop_sizer.Add(self.stopword_text, 1, wx.EXPAND)
        stop_sizer.Add(self.stopword_btn, 0)

        clean_sizer.Add(stop_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 自定义词典
        dict_sizer = wx.FlexGridSizer(0, 3, 5, 10)
        dict_sizer.AddGrowableCol(1)

        dict_label = wx.StaticText(clean_box, wx.ID_ANY, u"自定义词典:")
        self.dict_text = wx.TextCtrl(clean_box, wx.ID_ANY, u"",
                                     style=wx.TE_READONLY)
        self.dict_btn = wx.Button(clean_box, wx.ID_ANY, u"选择文件")

        dict_sizer.Add(dict_label, 0, wx.ALIGN_CENTER_VERTICAL)
        dict_sizer.Add(self.dict_text, 1, wx.EXPAND)
        dict_sizer.Add(self.dict_btn, 0)

        clean_sizer.Add(dict_sizer, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(clean_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # 预览区域
        preview_box = wx.StaticBox(self, wx.ID_ANY, u"文本预览（前1000字符）")
        preview_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)

        self.preview_text = wx.TextCtrl(preview_box, wx.ID_ANY, u"",
                                        style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.preview_text.SetMinSize((-1, 150))

        preview_sizer.Add(self.preview_text, 1, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(preview_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # 状态栏
        self.status_text = wx.StaticText(self, wx.ID_ANY, u"就绪")
        main_sizer.Add(self.status_text, 0, wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def bind_events(self):
        """绑定事件"""
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_files)
        self.remove_btn.Bind(wx.EVT_BUTTON, self.on_remove_files)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_files)
        self.import_btn.Bind(wx.EVT_BUTTON, self.on_import)
        self.stopword_btn.Bind(wx.EVT_BUTTON, self.on_select_stopwords)
        self.dict_btn.Bind(wx.EVT_BUTTON, self.on_select_dict)

    def on_add_files(self, event):
        """添加文件"""
        wildcard = u"所有支持格式 (*.txt;*.csv;*.xlsx;*.xls)|*.txt;*.csv;*.xlsx;*.xls|" \
                   u"TXT文件 (*.txt)|*.txt|" \
                   u"CSV文件 (*.csv)|*.csv|" \
                   u"Excel文件 (*.xlsx;*.xls)|*.xlsx;*.xls|" \
                   u"所有文件 (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message=u"选择要导入的文件",
            defaultDir=gl.CWD,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE
        )

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                if path not in self.imported_files:
                    self.imported_files.append(path)
                    self.file_list.Append(os.path.basename(path))

            self.status_text.SetLabel(u"已选择 {} 个文件".format(len(self.imported_files)))

        dlg.Destroy()

    def on_remove_files(self, event):
        """移除选中的文件"""
        selections = self.file_list.GetSelections()
        for idx in reversed(selections):
            del self.imported_files[idx]
            self.file_list.Delete(idx)

        self.status_text.SetLabel(u"已选择 {} 个文件".format(len(self.imported_files)))

    def on_clear_files(self, event):
        """清空文件列表"""
        self.imported_files = []
        self.file_list.Clear()
        self.status_text.SetLabel(u"就绪")

    def on_select_stopwords(self, event):
        """选择停用词文件"""
        wildcard = u"文本文件 (*.txt)|*.txt|所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(self, u"选择停用词文件", gl.CWD, "", wildcard, wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.stopword_text.SetValue(path)
            self.data_processor.load_stopwords(path)

        dlg.Destroy()

    def on_select_dict(self, event):
        """选择自定义词典"""
        wildcard = u"文本文件 (*.txt)|*.txt|所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(self, u"选择自定义词典", gl.CWD, "", wildcard, wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.dict_text.SetValue(path)
            self.data_processor.load_custom_dict(path)

        dlg.Destroy()

    def on_import(self, event):
        """开始导入"""
        if not self.imported_files:
            wx.MessageBox(u"请先添加要导入的文件", u"提示", wx.OK | wx.ICON_INFORMATION)
            return

        # 获取文本列配置
        col_text = self.col_text.GetValue().strip()
        text_column = None
        if col_text:
            try:
                text_column = int(col_text)
            except ValueError:
                text_column = col_text

        # 导入文件
        try:
            self.status_text.SetLabel(u"正在导入...")
            wx.BeginBusyCursor()

            content = self.data_processor.batch_import(self.imported_files, text_column)

            # 文本清洗
            cleaned = self.data_processor.clean_text(
                content,
                remove_punctuation=self.remove_punct_chk.GetValue(),
                remove_numbers=self.remove_num_chk.GetValue(),
                remove_spaces=self.remove_space_chk.GetValue(),
                remove_english=self.remove_eng_chk.GetValue(),
                lowercase=self.lowercase_chk.GetValue()
            )

            self.text_content = cleaned

            # 显示预览
            preview = cleaned[:1000] if len(cleaned) > 1000 else cleaned
            self.preview_text.SetValue(preview)

            # 保存到全局
            gl.IMPORTED_TEXT = cleaned

            wx.EndBusyCursor()
            self.status_text.SetLabel(u"导入完成，共 {} 字符".format(len(cleaned)))

            wx.MessageBox(u"导入成功！共导入 {} 个文件，总字符数: {}".format(
                len(self.imported_files), len(cleaned)),
                u"成功", wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            wx.EndBusyCursor()
            wx.MessageBox(u"导入失败: {}".format(str(e)), u"错误", wx.OK | wx.ICON_ERROR)
            self.status_text.SetLabel(u"导入失败")

    def set_import_type(self, file_type):
        """设置导入类型"""
        type_map = {
            'txt': 1,
            'csv': 2,
            'excel': 3
        }
        if file_type in type_map:
            self.file_type_choice.SetSelection(type_map[file_type])

    def set_batch_mode(self, enabled):
        """设置批量模式"""
        pass  # 当前已实现批量导入

    def get_imported_text(self):
        """获取导入的文本"""
        return self.text_content

    def get_data_processor(self):
        """获取数据处理器"""
        return self.data_processor
