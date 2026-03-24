# coding:utf-8
"""
词频分析页面 - 词频统计和可视化
"""

from __future__ import print_function, unicode_literals
import wx
import os
import sys

from Utils import gl
from Utils.data_processor import DataProcessor
from Utils.visualizer import WordFrequencyVisualizer, ColorScheme

# Python 2/3 兼容性
if sys.version_info[0] == 2:
    import cStringIO
else:
    from io import BytesIO as cStringIO


class MyWordFreq(wx.Panel):
    """词频分析页面"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))

        # 初始化
        self.data_processor = DataProcessor()
        self.visualizer = WordFrequencyVisualizer()
        self.word_freq = {}

        self.init_ui()
        self.bind_events()

    def init_ui(self):
        """初始化界面"""
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 左侧控制面板
        left_panel = wx.Panel(self)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # 数据源选择
        source_box = wx.StaticBox(left_panel, wx.ID_ANY, u"数据源")
        source_sizer = wx.StaticBoxSizer(source_box, wx.VERTICAL)

        self.use_imported_radio = wx.RadioButton(source_box, wx.ID_ANY,
                                                  u"使用已导入的数据")
        self.use_file_radio = wx.RadioButton(source_box, wx.ID_ANY,
                                              u"从文件加载")
        self.use_imported_radio.SetValue(True)

        source_sizer.Add(self.use_imported_radio, 0, wx.ALL, 5)

        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_sizer.Add(self.use_file_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        self.file_text = wx.TextCtrl(source_box, wx.ID_ANY, u"",
                                      style=wx.TE_READONLY)
        self.file_btn = wx.Button(source_box, wx.ID_ANY, u"浏览...")
        file_sizer.Add(self.file_text, 1, wx.EXPAND | wx.LEFT, 5)
        file_sizer.Add(self.file_btn, 0, wx.LEFT, 5)

        source_sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(source_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 分析配置
        config_box = wx.StaticBox(left_panel, wx.ID_ANY, u"分析配置")
        config_sizer = wx.StaticBoxSizer(config_box, wx.VERTICAL)

        # 显示数量
        topn_sizer = wx.FlexGridSizer(0, 2, 5, 10)
        topn_sizer.AddGrowableCol(1)

        topn_label = wx.StaticText(config_box, wx.ID_ANY, u"显示词数:")
        self.topn_spin = wx.SpinCtrl(config_box, wx.ID_ANY, "20",
                                      min=5, max=100)

        topn_sizer.Add(topn_label, 0, wx.ALIGN_CENTER_VERTICAL)
        topn_sizer.Add(self.topn_spin, 1, wx.EXPAND)

        # 颜色方案
        color_label = wx.StaticText(config_box, wx.ID_ANY, u"颜色方案:")
        self.color_choice = wx.Choice(config_box, wx.ID_ANY,
                                       choices=ColorScheme.get_all_schemes())
        self.color_choice.SetSelection(0)

        topn_sizer.Add(color_label, 0, wx.ALIGN_CENTER_VERTICAL)
        topn_sizer.Add(self.color_choice, 1, wx.EXPAND)

        # 图表方向
        orient_label = wx.StaticText(config_box, wx.ID_ANY, u"图表方向:")
        self.orient_choice = wx.Choice(config_box, wx.ID_ANY,
                                        choices=[u"水平柱状图", u"垂直柱状图"])
        self.orient_choice.SetSelection(0)

        topn_sizer.Add(orient_label, 0, wx.ALIGN_CENTER_VERTICAL)
        topn_sizer.Add(self.orient_choice, 1, wx.EXPAND)

        config_sizer.Add(topn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(config_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 操作按钮
        btn_sizer = wx.BoxSizer(wx.VERTICAL)

        self.analyze_btn = wx.Button(left_panel, wx.ID_ANY, u"开始分析")
        self.analyze_btn.SetBackgroundColour(wx.Colour(0, 120, 215))
        self.analyze_btn.SetForegroundColour(wx.Colour(255, 255, 255))

        self.export_chart_btn = wx.Button(left_panel, wx.ID_ANY, u"导出图表")
        self.export_list_btn = wx.Button(left_panel, wx.ID_ANY, u"导出词频表")

        btn_sizer.Add(self.analyze_btn, 0, wx.EXPAND | wx.ALL, 5)
        btn_sizer.Add(self.export_chart_btn, 0, wx.EXPAND | wx.ALL, 5)
        btn_sizer.Add(self.export_list_btn, 0, wx.EXPAND | wx.ALL, 5)

        left_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 统计信息
        stats_box = wx.StaticBox(left_panel, wx.ID_ANY, u"统计信息")
        stats_sizer = wx.StaticBoxSizer(stats_box, wx.VERTICAL)

        self.stats_text = wx.StaticText(stats_box, wx.ID_ANY,
                                         u"总词数: 0\n唯一词数: 0\n平均词频: 0")
        stats_sizer.Add(self.stats_text, 0, wx.ALL, 5)

        left_sizer.Add(stats_sizer, 0, wx.EXPAND | wx.ALL, 5)

        left_panel.SetSizer(left_sizer)
        main_sizer.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)

        # 右侧显示区域
        right_panel = wx.Panel(self)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # 图表显示
        chart_box = wx.StaticBox(right_panel, wx.ID_ANY, u"词频图表")
        chart_sizer = wx.StaticBoxSizer(chart_box, wx.VERTICAL)

        self.chart_bitmap = wx.StaticBitmap(chart_box, wx.ID_ANY,
                                            wx.Bitmap(600, 350))
        chart_sizer.Add(self.chart_bitmap, 1, wx.EXPAND | wx.ALL, 5)

        right_sizer.Add(chart_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # 词频列表
        list_box = wx.StaticBox(right_panel, wx.ID_ANY, u"词频列表")
        list_sizer = wx.StaticBoxSizer(list_box, wx.VERTICAL)

        self.freq_list = wx.ListCtrl(list_box, wx.ID_ANY,
                                      style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.freq_list.AppendColumn(u"排名", width=60)
        self.freq_list.AppendColumn(u"词语", width=150)
        self.freq_list.AppendColumn(u"频次", width=100)
        self.freq_list.AppendColumn(u"占比", width=100)
        self.freq_list.SetMinSize((-1, 200))

        list_sizer.Add(self.freq_list, 1, wx.EXPAND | wx.ALL, 5)

        right_sizer.Add(list_sizer, 1, wx.EXPAND | wx.ALL, 5)

        right_panel.SetSizer(right_sizer)
        main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def bind_events(self):
        """绑定事件"""
        self.file_btn.Bind(wx.EVT_BUTTON, self.on_select_file)
        self.analyze_btn.Bind(wx.EVT_BUTTON, self.on_analyze)
        self.export_chart_btn.Bind(wx.EVT_BUTTON, self.on_export_chart)
        self.export_list_btn.Bind(wx.EVT_BUTTON, self.on_export_list)
        self.color_choice.Bind(wx.EVT_CHOICE, self.on_color_changed)

    def on_select_file(self, event):
        """选择文件"""
        wildcard = u"所有支持格式 (*.txt;*.csv;*.xlsx;*.xls)|*.txt;*.csv;*.xlsx;*.xls|" \
                   u"TXT文件 (*.txt)|*.txt|" \
                   u"CSV文件 (*.csv)|*.csv|" \
                   u"Excel文件 (*.xlsx;*.xls)|*.xlsx;*.xls|" \
                   u"所有文件 (*.*)|*.*"

        dlg = wx.FileDialog(self, u"选择文件", gl.CWD, "", wildcard, wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            self.file_text.SetValue(dlg.GetPath())

        dlg.Destroy()

    def on_analyze(self, event):
        """开始分析"""
        try:
            wx.BeginBusyCursor()

            # 获取数据源
            if self.use_imported_radio.GetValue():
                # 使用已导入的数据
                if hasattr(gl, 'IMPORTED_TEXT') and gl.IMPORTED_TEXT:
                    text = gl.IMPORTED_TEXT
                else:
                    wx.EndBusyCursor()
                    wx.MessageBox(u"没有已导入的数据，请先导入文件",
                                  u"提示", wx.OK | wx.ICON_INFORMATION)
                    return
            else:
                # 从文件加载
                filepath = self.file_text.GetValue()
                if not filepath:
                    wx.EndBusyCursor()
                    wx.MessageBox(u"请选择文件", u"提示", wx.OK | wx.ICON_INFORMATION)
                    return

                text = self.data_processor.import_file(filepath)
                text = self.data_processor.clean_text(text)

            # 分词
            words = self.data_processor.segment_text(text)

            # 统计词频
            self.word_freq = self.data_processor.get_word_frequency(words, top_n=200)

            # 更新显示
            self.update_chart()
            self.update_list()
            self.update_stats(words)

            wx.EndBusyCursor()

        except Exception as e:
            wx.EndBusyCursor()
            wx.MessageBox(u"分析失败: {}".format(str(e)), u"错误", wx.OK | wx.ICON_ERROR)

    def update_chart(self):
        """更新图表"""
        if not self.word_freq:
            return

        # 获取配置
        top_n = self.topn_spin.GetValue()
        color_scheme = self.color_choice.GetString(self.color_choice.GetSelection())
        horizontal = self.orient_choice.GetSelection() == 0

        # 设置颜色方案
        self.visualizer.set_color_scheme(color_scheme)

        # 生成图表
        try:
            bitmap = self.visualizer.get_bar_chart_bitmap(
                self.word_freq, top_n=top_n,
                title=u'词频统计TOP{}'.format(top_n),
                horizontal=horizontal
            )
            self.chart_bitmap.SetBitmap(bitmap)
            self.Layout()
        except Exception as e:
            print("Chart update error:", e)

    def update_list(self):
        """更新词频列表"""
        self.freq_list.DeleteAllItems()

        if not self.word_freq:
            return

        sorted_words = sorted(self.word_freq.items(), key=lambda x: x[1], reverse=True)
        total_freq = sum(self.word_freq.values())

        for i, (word, freq) in enumerate(sorted_words, 1):
            percentage = '{:.2f}%'.format(100.0 * freq / total_freq) if total_freq > 0 else '0.00%'
            index = self.freq_list.InsertItem(i-1, str(i))
            self.freq_list.SetItem(index, 1, word)
            self.freq_list.SetItem(index, 2, str(freq))
            self.freq_list.SetItem(index, 3, percentage)

    def update_stats(self, words):
        """更新统计信息"""
        total = len(words)
        unique = len(self.word_freq)
        avg = sum(self.word_freq.values()) / float(unique) if unique > 0 else 0

        stats = u"总词数: {}\n唯一词数: {}\n平均词频: {:.2f}".format(total, unique, avg)
        self.stats_text.SetLabel(stats)

    def on_color_changed(self, event):
        """颜色方案改变"""
        if self.word_freq:
            self.update_chart()

    def on_export_chart(self, event):
        """导出图表"""
        if not self.word_freq:
            wx.MessageBox(u"请先进行分析", u"提示", wx.OK | wx.ICON_INFORMATION)
            return

        wildcard = u"PNG图片 (*.png)|*.png|JPEG图片 (*.jpg)|*.jpg|所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(self, u"保存图表", gl.CWD, "wordfreq_chart.png",
                            wildcard, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            try:
                path = dlg.GetPath()
                top_n = self.topn_spin.GetValue()
                color_scheme = self.color_choice.GetString(self.color_choice.GetSelection())
                horizontal = self.orient_choice.GetSelection() == 0

                self.visualizer.set_color_scheme(color_scheme)
                self.visualizer.save_bar_chart(
                    self.word_freq, path, top_n=top_n,
                    title=u'词频统计TOP{}'.format(top_n),
                    horizontal=horizontal
                )

                wx.MessageBox(u"图表已保存", u"成功", wx.OK | wx.ICON_INFORMATION)

            except Exception as e:
                wx.MessageBox(u"保存失败: {}".format(str(e)), u"错误", wx.OK | wx.ICON_ERROR)

        dlg.Destroy()

    def on_export_list(self, event):
        """导出词频列表"""
        if not self.word_freq:
            wx.MessageBox(u"请先进行分析", u"提示", wx.OK | wx.ICON_INFORMATION)
            return

        wildcard = u"CSV文件 (*.csv)|*.csv|TXT文件 (*.txt)|*.txt|所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(self, u"保存词频表", gl.CWD, "wordfreq_list.csv",
                            wildcard, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            try:
                path = dlg.GetPath()
                ext = os.path.splitext(path)[1].lower()

                sorted_words = sorted(self.word_freq.items(), key=lambda x: x[1], reverse=True)
                total_freq = sum(self.word_freq.values())

                if ext == '.csv':
                    import csv
                    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow([u'排名', u'词语', u'频次', u'占比'])
                        for i, (word, freq) in enumerate(sorted_words, 1):
                            percentage = '{:.2f}%'.format(100.0 * freq / total_freq) if total_freq > 0 else '0.00%'
                            writer.writerow([i, word, freq, percentage])
                else:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(u'排名\t词语\t频次\t占比\n')
                        for i, (word, freq) in enumerate(sorted_words, 1):
                            percentage = '{:.2f}%'.format(100.0 * freq / total_freq) if total_freq > 0 else '0.00%'
                            f.write(u'{0}\t{1}\t{2}\t{3}\n'.format(i, word, freq, percentage))

                wx.MessageBox(u"词频表已保存", u"成功", wx.OK | wx.ICON_INFORMATION)

            except Exception as e:
                wx.MessageBox(u"保存失败: {}".format(str(e)), u"错误", wx.OK | wx.ICON_ERROR)

        dlg.Destroy()

    def on_page_active(self):
        """页面激活时调用"""
        pass
