# coding:utf-8
"""
批量处理页面 - 批量导入文件并生成词云
"""

from __future__ import print_function, unicode_literals
import wx
import os
import sys
import threading

from Utils import gl
from Utils.data_processor import DataProcessor, BatchProcessor
from Utils.new_wordcloud import MyWordCloud
from Utils.visualizer import ColorScheme
from Utils.exporter import ExportManager

# Python 2/3 兼容性
if sys.version_info[0] == 2:
    import cStringIO
else:
    from io import BytesIO as cStringIO


class MyBatch(wx.Panel):
    """批量处理页面"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))

        # 初始化
        self.data_processor = DataProcessor()
        self.batch_processor = BatchProcessor(self.data_processor)
        self.export_manager = ExportManager()
        self.file_list = []
        self.output_dir = ""
        self.is_processing = False

        self.init_ui()
        self.bind_events()

    def init_ui(self):
        """初始化界面"""
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 左侧面板
        left_panel = wx.Panel(self)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # 文件列表区域
        file_box = wx.StaticBox(left_panel, wx.ID_ANY, u"文件列表")
        file_sizer = wx.StaticBoxSizer(file_box, wx.VERTICAL)

        self.file_listctrl = wx.ListCtrl(file_box, wx.ID_ANY,
                                          style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.file_listctrl.AppendColumn(u"文件名", width=200)
        self.file_listctrl.AppendColumn(u"状态", width=80)
        self.file_listctrl.SetMinSize((300, 200))

        file_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_btn = wx.Button(file_box, wx.ID_ANY, u"添加文件")
        self.remove_btn = wx.Button(file_box, wx.ID_ANY, u"移除")
        self.clear_btn = wx.Button(file_box, wx.ID_ANY, u"清空")

        file_btn_sizer.Add(self.add_btn, 1, wx.ALL, 2)
        file_btn_sizer.Add(self.remove_btn, 1, wx.ALL, 2)
        file_btn_sizer.Add(self.clear_btn, 1, wx.ALL, 2)

        file_sizer.Add(self.file_listctrl, 1, wx.EXPAND | wx.ALL, 5)
        file_sizer.Add(file_btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        left_sizer.Add(file_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # 输出设置
        output_box = wx.StaticBox(left_panel, wx.ID_ANY, u"输出设置")
        output_sizer = wx.StaticBoxSizer(output_box, wx.VERTICAL)

        dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dir_label = wx.StaticText(output_box, wx.ID_ANY, u"输出目录:")
        self.dir_text = wx.TextCtrl(output_box, wx.ID_ANY, u"",
                                     style=wx.TE_READONLY)
        self.dir_btn = wx.Button(output_box, wx.ID_ANY, u"浏览...")

        dir_sizer.Add(dir_label, 0, wx.ALIGN_CENTER_VERTICAL)
        dir_sizer.Add(self.dir_text, 1, wx.EXPAND | wx.LEFT, 5)
        dir_sizer.Add(self.dir_btn, 0, wx.LEFT, 5)

        output_sizer.Add(dir_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 输出格式
        format_sizer = wx.FlexGridSizer(0, 2, 5, 10)
        format_label = wx.StaticText(output_box, wx.ID_ANY, u"输出格式:")
        self.format_choice = wx.Choice(output_box, wx.ID_ANY,
                                        choices=["PNG", "JPG", "PDF", "SVG"])
        self.format_choice.SetSelection(0)

        format_sizer.Add(format_label, 0, wx.ALIGN_CENTER_VERTICAL)
        format_sizer.Add(self.format_choice, 1, wx.EXPAND)

        # 分辨率
        dpi_label = wx.StaticText(output_box, wx.ID_ANY, u"DPI分辨率:")
        self.dpi_spin = wx.SpinCtrl(output_box, wx.ID_ANY, "300",
                                     min=72, max=600)

        format_sizer.Add(dpi_label, 0, wx.ALIGN_CENTER_VERTICAL)
        format_sizer.Add(self.dpi_spin, 1, wx.EXPAND)

        output_sizer.Add(format_sizer, 0, wx.EXPAND | wx.ALL, 5)

        left_sizer.Add(output_sizer, 0, wx.EXPAND | wx.ALL, 5)

        left_panel.SetSizer(left_sizer)
        main_sizer.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)

        # 右侧面板
        right_panel = wx.Panel(self)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # 词云配置
        config_box = wx.StaticBox(right_panel, wx.ID_ANY, u"词云配置")
        config_sizer = wx.StaticBoxSizer(config_box, wx.VERTICAL)

        config_grid = wx.FlexGridSizer(0, 4, 5, 10)
        config_grid.AddGrowableCol(1)
        config_grid.AddGrowableCol(3)

        # 字体
        font_label = wx.StaticText(config_box, wx.ID_ANY, u"字体:")
        self.font_choice = wx.Choice(config_box, wx.ID_ANY, choices=[])

        config_grid.Add(font_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_grid.Add(self.font_choice, 1, wx.EXPAND)

        # 背景色
        bg_label = wx.StaticText(config_box, wx.ID_ANY, u"背景色:")
        self.bg_color = wx.ColourPickerCtrl(config_box, wx.ID_ANY, wx.WHITE)

        config_grid.Add(bg_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        config_grid.Add(self.bg_color, 1, wx.EXPAND)

        # 宽度
        width_label = wx.StaticText(config_box, wx.ID_ANY, u"宽度:")
        self.width_spin = wx.SpinCtrl(config_box, wx.ID_ANY, "800",
                                       min=100, max=5000)

        config_grid.Add(width_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_grid.Add(self.width_spin, 1, wx.EXPAND)

        # 高度
        height_label = wx.StaticText(config_box, wx.ID_ANY, u"高度:")
        self.height_spin = wx.SpinCtrl(config_box, wx.ID_ANY, "600",
                                        min=100, max=5000)

        config_grid.Add(height_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        config_grid.Add(self.height_spin, 1, wx.EXPAND)

        # 最大字体
        maxfont_label = wx.StaticText(config_box, wx.ID_ANY, u"最大字体:")
        self.maxfont_spin = wx.SpinCtrl(config_box, wx.ID_ANY, "100",
                                          min=10, max=500)

        config_grid.Add(maxfont_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_grid.Add(self.maxfont_spin, 1, wx.EXPAND)

        # 最小字体
        minfont_label = wx.StaticText(config_box, wx.ID_ANY, u"最小字体:")
        self.minfont_spin = wx.SpinCtrl(config_box, wx.ID_ANY, "10",
                                          min=4, max=100)

        config_grid.Add(minfont_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        config_grid.Add(self.minfont_spin, 1, wx.EXPAND)

        config_sizer.Add(config_grid, 0, wx.EXPAND | wx.ALL, 5)

        # 停用词
        stop_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stop_chk_label = wx.StaticText(config_box, wx.ID_ANY, u"停用词表:")
        self.stopword_text = wx.TextCtrl(config_box, wx.ID_ANY, u"",
                                          style=wx.TE_READONLY)
        self.stopword_btn = wx.Button(config_box, wx.ID_ANY, u"选择...")

        stop_sizer.Add(stop_chk_label, 0, wx.ALIGN_CENTER_VERTICAL)
        stop_sizer.Add(self.stopword_text, 1, wx.EXPAND | wx.LEFT, 5)
        stop_sizer.Add(self.stopword_btn, 0, wx.LEFT, 5)

        config_sizer.Add(stop_sizer, 0, wx.EXPAND | wx.ALL, 5)

        right_sizer.Add(config_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 进度区域
        progress_box = wx.StaticBox(right_panel, wx.ID_ANY, u"处理进度")
        progress_sizer = wx.StaticBoxSizer(progress_box, wx.VERTICAL)

        self.progress_gauge = wx.Gauge(progress_box, wx.ID_ANY, 100)
        progress_sizer.Add(self.progress_gauge, 0, wx.EXPAND | wx.ALL, 5)

        self.progress_text = wx.StaticText(progress_box, wx.ID_ANY, u"就绪")
        progress_sizer.Add(self.progress_text, 0, wx.ALL, 5)

        # 日志显示
        self.log_text = wx.TextCtrl(progress_box, wx.ID_ANY, u"",
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.log_text.SetMinSize((-1, 150))
        progress_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)

        right_sizer.Add(progress_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # 操作按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.start_btn = wx.Button(right_panel, wx.ID_ANY, u"开始批量处理")
        self.start_btn.SetBackgroundColour(wx.Colour(0, 120, 215))
        self.start_btn.SetForegroundColour(wx.Colour(255, 255, 255))

        self.stop_btn = wx.Button(right_panel, wx.ID_ANY, u"停止")
        self.stop_btn.Enable(False)

        btn_sizer.Add(self.start_btn, 1, wx.ALL, 5)
        btn_sizer.Add(self.stop_btn, 0, wx.ALL, 5)

        right_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        right_panel.SetSizer(right_sizer)
        main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def bind_events(self):
        """绑定事件"""
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_files)
        self.remove_btn.Bind(wx.EVT_BUTTON, self.on_remove_file)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_files)
        self.dir_btn.Bind(wx.EVT_BUTTON, self.on_select_output_dir)
        self.stopword_btn.Bind(wx.EVT_BUTTON, self.on_select_stopwords)
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start_batch)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_batch)

    def on_add_files(self, event):
        """添加文件"""
        wildcard = u"所有支持格式 (*.txt;*.csv;*.xlsx;*.xls)|*.txt;*.csv;*.xlsx;*.xls|" \
                   u"TXT文件 (*.txt)|*.txt|" \
                   u"CSV文件 (*.csv)|*.csv|" \
                   u"Excel文件 (*.xlsx;*.xls)|*.xlsx;*.xls|" \
                   u"所有文件 (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message=u"选择要处理的文件",
            defaultDir=gl.CWD,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE
        )

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                if path not in self.file_list:
                    self.file_list.append(path)
                    index = self.file_listctrl.InsertItem(
                        self.file_listctrl.GetItemCount(),
                        os.path.basename(path)
                    )
                    self.file_listctrl.SetItem(index, 1, u"待处理")

        dlg.Destroy()

    def on_remove_file(self, event):
        """移除选中的文件"""
        selected = self.file_listctrl.GetFirstSelected()
        while selected != -1:
            del self.file_list[selected]
            self.file_listctrl.DeleteItem(selected)
            selected = self.file_listctrl.GetFirstSelected()

    def on_clear_files(self, event):
        """清空文件列表"""
        self.file_list = []
        self.file_listctrl.DeleteAllItems()

    def on_select_output_dir(self, event):
        """选择输出目录"""
        dlg = wx.DirDialog(self, u"选择输出目录", gl.CWD)

        if dlg.ShowModal() == wx.ID_OK:
            self.output_dir = dlg.GetPath()
            self.dir_text.SetValue(self.output_dir)

        dlg.Destroy()

    def on_select_stopwords(self, event):
        """选择停用词文件"""
        wildcard = u"文本文件 (*.txt)|*.txt|所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(self, u"选择停用词文件", gl.CWD, "", wildcard, wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.stopword_text.SetValue(path)

        dlg.Destroy()

    def on_start_batch(self, event):
        """开始批量处理"""
        if not self.file_list:
            wx.MessageBox(u"请先添加要处理的文件", u"提示", wx.OK | wx.ICON_INFORMATION)
            return

        if not self.output_dir:
            wx.MessageBox(u"请选择输出目录", u"提示", wx.OK | wx.ICON_INFORMATION)
            return

        # 获取配置
        wordcloud_config = {
            'font_path': self.get_font_path(),
            'background_color': self.get_bg_color(),
            'width': self.width_spin.GetValue(),
            'height': self.height_spin.GetValue(),
            'max_font_size': self.maxfont_spin.GetValue(),
            'min_font_size': self.minfont_spin.GetValue()
        }

        # 加载停用词
        stopword_file = self.stopword_text.GetValue()
        if stopword_file and os.path.exists(stopword_file):
            self.data_processor.load_stopwords(stopword_file)
        else:
            self.data_processor.load_stopwords()

        # 开始处理
        self.is_processing = True
        self.start_btn.Enable(False)
        self.stop_btn.Enable(True)
        self.progress_gauge.SetValue(0)
        self.log_text.Clear()

        # 在后台线程中处理
        thread = threading.Thread(
            target=self.process_batch,
            args=(wordcloud_config,)
        )
        thread.daemon = True
        thread.start()

    def on_stop_batch(self, event):
        """停止批量处理"""
        self.is_processing = False
        self.progress_text.SetLabel(u"正在停止...")

    def process_batch(self, wordcloud_config):
        """批量处理"""
        total = len(self.file_list)
        success_count = 0
        fail_count = 0

        for i, filepath in enumerate(self.file_list):
            if not self.is_processing:
                break

            # 更新进度
            wx.CallAfter(self.update_progress, i, total,
                         u"正在处理: {}".format(os.path.basename(filepath)))

            try:
                # 导入文件
                self.data_processor.import_file(filepath)

                # 清洗文本
                cleaned = self.data_processor.clean_text()

                # 分词
                words = self.data_processor.segment_text(cleaned)

                # 统计词频
                word_freq = self.data_processor.get_word_frequency(words, top_n=200)

                # 生成词云
                wc = MyWordCloud()
                wordcloud = wc.GenWordCloud(
                    seg_list=word_freq,
                    font_path=wordcloud_config['font_path'],
                    background_color=wordcloud_config['background_color'],
                    width=wordcloud_config['width'],
                    height=wordcloud_config['height'],
                    flag=0
                )

                # 保存文件
                filename = os.path.splitext(os.path.basename(filepath))[0]
                output_format = self.format_choice.GetString(
                    self.format_choice.GetSelection()
                ).lower()

                output_path = os.path.join(
                    self.output_dir,
                    "{}_wordcloud.{}".format(filename, output_format)
                )

                self.export_manager.export_wordcloud(
                    wordcloud, output_path, format=output_format
                )

                success_count += 1
                wx.CallAfter(self.update_file_status, i, u"成功")
                wx.CallAfter(self.append_log, u"[成功] {} -> {}".format(
                    os.path.basename(filepath), output_path))

            except Exception as e:
                fail_count += 1
                wx.CallAfter(self.update_file_status, i, u"失败")
                wx.CallAfter(self.append_log, u"[失败] {}: {}".format(
                    os.path.basename(filepath), str(e)))

        # 处理完成
        wx.CallAfter(self.batch_finished, success_count, fail_count)

    def update_progress(self, current, total, message):
        """更新进度"""
        progress = int(100.0 * (current + 1) / total)
        self.progress_gauge.SetValue(progress)
        self.progress_text.SetLabel(message)

    def update_file_status(self, index, status):
        """更新文件状态"""
        self.file_listctrl.SetItem(index, 1, status)

    def append_log(self, message):
        """添加日志"""
        self.log_text.AppendText(message + "\n")

    def batch_finished(self, success, fail):
        """批量处理完成"""
        self.is_processing = False
        self.start_btn.Enable(True)
        self.stop_btn.Enable(False)
        self.progress_gauge.SetValue(100)
        self.progress_text.SetLabel(u"处理完成")

        wx.MessageBox(u"批量处理完成！\n成功: {}\n失败: {}".format(success, fail),
                      u"完成", wx.OK | wx.ICON_INFORMATION)

    def get_font_path(self):
        """获取字体路径"""
        font_name = self.font_choice.GetString(self.font_choice.GetSelection())
        if font_name:
            return os.path.join(gl.CWD, "data", "font", font_name + ".ttf")
        return None

    def get_bg_color(self):
        """获取背景色"""
        color = self.bg_color.GetColour()
        return '#{:02x}{:02x}{:02x}'.format(color.Red(), color.Green(), color.Blue())

    def update_Choice(self):
        """更新字体选择"""
        font_dir = os.path.join(gl.CWD, "data", "font")
        if os.path.exists(font_dir):
            fonts = [f[:-4] for f in os.listdir(font_dir) if f.endswith('.ttf')]
            self.font_choice.Clear()
            self.font_choice.AppendItems(fonts)
            if fonts:
                self.font_choice.SetSelection(0)

    def on_page_active(self):
        """页面激活时调用"""
        self.update_Choice()
