# coding:utf-8

import wx
from Utils import gl, new_wordcloud, exporter, cleaner
import io
import os


class MyWeb(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        self.stop_word_file = None
        self.goal_file = None
        self.final_pic = None
        self.word_freq = []
        
        self.InitUI()
    
    def InitUI(self):
        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "词云配置"), wx.HORIZONTAL)

        sbSizer4 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, "目标文件"), wx.VERTICAL)

        fgSizer4 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.StopWords_Button = wx.Button(sbSizer4.GetStaticBox(), wx.ID_ANY, "打开停词表", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        fgSizer4.Add(self.StopWords_Button, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.StopWords_staticText = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, "当前：默认", wx.DefaultPosition,
                                                  wx.DefaultSize, 0)
        self.StopWords_staticText.Wrap(-1)
        self.StopWords_staticText.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

        fgSizer4.Add(self.StopWords_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.GoalFile_Button = wx.Button(sbSizer4.GetStaticBox(), wx.ID_ANY, "打开Web文件", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        fgSizer4.Add(self.GoalFile_Button, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.GoalFile_staticText = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, "当前：无", wx.DefaultPosition,
                                                 wx.DefaultSize, 0)
        self.GoalFile_staticText.Wrap(-1)
        self.GoalFile_staticText.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

        fgSizer4.Add(self.GoalFile_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sbSizer4.Add(fgSizer4, 1, wx.EXPAND, 5)

        sbSizer1.Add(sbSizer4, 1, wx.EXPAND, 5)

        sbSizer5 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, "尺寸设置"), wx.VERTICAL)

        fgSizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer2.SetFlexibleDirection(wx.BOTH)
        fgSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.Margin_staticText = wx.StaticText(sbSizer5.GetStaticBox(), wx.ID_ANY, "边距", wx.DefaultPosition,
                                               wx.DefaultSize, 0)
        self.Margin_staticText.Wrap(-1)
        fgSizer2.Add(self.Margin_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.Margin_spinCtrl = wx.SpinCtrl(sbSizer5.GetStaticBox(), wx.ID_ANY, "5", wx.DefaultPosition,
                                           wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 50, 5)
        fgSizer2.Add(self.Margin_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.Width_staticText = wx.StaticText(sbSizer5.GetStaticBox(), wx.ID_ANY, "宽度", wx.DefaultPosition,
                                              wx.DefaultSize, 0)
        self.Width_staticText.Wrap(-1)
        fgSizer2.Add(self.Width_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.Width_spinCtrl = wx.SpinCtrl(sbSizer5.GetStaticBox(), wx.ID_ANY, "800", wx.DefaultPosition,
                                          wx.DefaultSize, wx.SP_ARROW_KEYS, 100, 10000, 800)
        fgSizer2.Add(self.Width_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.Height_staticText = wx.StaticText(sbSizer5.GetStaticBox(), wx.ID_ANY, "高度", wx.DefaultPosition,
                                               wx.DefaultSize, 0)
        self.Height_staticText.Wrap(-1)
        fgSizer2.Add(self.Height_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.Height_spinCtrl = wx.SpinCtrl(sbSizer5.GetStaticBox(), wx.ID_ANY, "600", wx.DefaultPosition,
                                           wx.DefaultSize, wx.SP_ARROW_KEYS, 80, 10000, 600)
        fgSizer2.Add(self.Height_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sbSizer5.Add(fgSizer2, 1, wx.EXPAND, 5)

        sbSizer1.Add(sbSizer5, 1, wx.EXPAND, 5)

        sbSizer6 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, "字体设置"), wx.VERTICAL)

        fgSizer3 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer3.SetFlexibleDirection(wx.BOTH)
        fgSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.Font_staticText = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, "选择字体", wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.Font_staticText.Wrap(-1)
        fgSizer3.Add(self.Font_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        Font_ChoiceChoices = []
        self.Font_Choice = wx.Choice(sbSizer6.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                   Font_ChoiceChoices, 0)
        self.update_Choice()
        fgSizer3.Add(self.Font_Choice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.MaxFont_staticText = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, "最大字体", wx.DefaultPosition,
                                                wx.DefaultSize, 0)
        self.MaxFont_staticText.Wrap(-1)
        fgSizer3.Add(self.MaxFont_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.MaxFont_spinCtrl = wx.SpinCtrl(sbSizer6.GetStaticBox(), wx.ID_ANY, "40", wx.DefaultPosition,
                                            wx.DefaultSize, wx.SP_ARROW_KEYS, 10, 200, 40)
        fgSizer3.Add(self.MaxFont_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.MinFont_staticText = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, "最小字体", wx.DefaultPosition,
                                                wx.DefaultSize, 0)
        self.MinFont_staticText.Wrap(-1)
        fgSizer3.Add(self.MinFont_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.MinFont_spinCtrl = wx.SpinCtrl(sbSizer6.GetStaticBox(), wx.ID_ANY, "10", wx.DefaultPosition,
                                            wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 100, 10)
        fgSizer3.Add(self.MinFont_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sbSizer6.Add(fgSizer3, 1, wx.EXPAND, 5)

        sbSizer1.Add(sbSizer6, 1, wx.EXPAND, 5)

        sbSizer7 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, "颜色设置"), wx.VERTICAL)

        self.BG_Color_staticText = wx.StaticText(sbSizer7.GetStaticBox(), wx.ID_ANY, "选择背景颜色", wx.DefaultPosition,
                                                 wx.DefaultSize, 0)
        self.BG_Color_staticText.Wrap(-1)
        sbSizer7.Add(self.BG_Color_staticText, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.BG_Color_colourPicker = wx.ColourPickerCtrl(sbSizer7.GetStaticBox(), wx.ID_ANY, wx.BLACK,
                                                         wx.DefaultPosition,
                                                         wx.DefaultSize, wx.CLRP_DEFAULT_STYLE)
        sbSizer7.Add(self.BG_Color_colourPicker, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        sbSizer1.Add(sbSizer7, 1, wx.EXPAND, 5)

        bSizer1.Add(sbSizer1, 1, wx.EXPAND, 5)

        sbSizer3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "词云生成"), wx.VERTICAL)

        fgSizer1 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.GenWordCloud_Button = wx.Button(sbSizer3.GetStaticBox(), wx.ID_ANY, "词云生成", wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        bSizer2.Add(self.GenWordCloud_Button, 0, wx.ALL, 5)

        self.Save_Button = wx.Button(sbSizer3.GetStaticBox(), wx.ID_ANY, "保存词云", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.Save_Button, 0, wx.ALL, 5)
        
        self.Export_Button = wx.Button(sbSizer3.GetStaticBox(), wx.ID_ANY, "导出报告", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.Export_Button, 0, wx.ALL, 5)

        fgSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        sbSizer9 = wx.StaticBoxSizer(wx.StaticBox(sbSizer3.GetStaticBox(), wx.ID_ANY, "词云预览"), wx.VERTICAL)

        self.PicShow_Bitmap = wx.StaticBitmap(sbSizer9.GetStaticBox(), wx.ID_ANY,
                                              wx.Bitmap(400, 300), wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer9.Add(self.PicShow_Bitmap, 1, wx.ALL | wx.EXPAND, 5)

        fgSizer1.Add(sbSizer9, 1, wx.EXPAND, 5)

        sbSizer3.Add(fgSizer1, 1, wx.EXPAND, 5)

        bSizer1.Add(sbSizer3, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.StopWords_Button.Bind(wx.EVT_BUTTON, self.StopWords_ButtonOnButtonClick)
        self.GoalFile_Button.Bind(wx.EVT_BUTTON, self.GoalFile_ButtonOnButtonClick)
        self.GenWordCloud_Button.Bind(wx.EVT_BUTTON, self.GenWordCloud_ButtonOnButtonClick)
        self.Save_Button.Bind(wx.EVT_BUTTON, self.Save_ButtonOnButtonClick)
        self.Export_Button.Bind(wx.EVT_BUTTON, self.Export_ButtonOnButtonClick)

    def StopWords_ButtonOnButtonClick(self, event):
        wildcard = "TXT纯文本 (*.txt)|*.txt"

        dlg = wx.FileDialog(
            self, message="选取停词表文档",
            defaultDir=gl.get_data_path('stopwords'),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.stop_word_file = path
            self.StopWords_staticText.SetLabelText(os.path.basename(path))
        dlg.Destroy()

    def GoalFile_ButtonOnButtonClick(self, event):
        wildcard = "HTML文本 (*.html;*.htm)|*.html;*.htm"

        dlg = wx.FileDialog(
            self, message="选取词云生成目标文档",
            defaultDir=gl.CWD,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.goal_file = path
            self.GoalFile_staticText.SetLabelText(os.path.basename(path))

        dlg.Destroy()

    def GenWordCloud_ButtonOnButtonClick(self, event):
        stop_word_file, goal_file, margin, width, height, font, font_max, font_min, bg_color = self.GetConf()
        
        if goal_file is None:
            dlg = wx.MessageDialog(self, "请先选取目标文档",
                                "文件缺失",
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        wc = new_wordcloud.MyWordCloud()
        
        if stop_word_file:
            wc.load_stopwords(stop_word_file)
        else:
            default_stopwords = gl.get_stopwords_path('cn')
            if os.path.exists(default_stopwords):
                wc.load_stopwords(default_stopwords)
        
        html_text = cleaner.clean_html(open(goal_file, 'r', encoding='utf-8').read())
        
        output_file_name = os.path.join(gl.get_catch_dir(), "tmp_web_file.txt")
        with open(output_file_name, 'w', encoding='utf-8') as f:
            f.write(html_text.strip())
        
        print("构建分词表")
        words = wc.cut_text(html_text)
        self.word_freq = wc.get_word_frequency()
        
        font_path = gl.get_font_path(font) if font else None
        
        print("生成词云")
        self.final_pic = wc.generate_wordcloud(
            word_freq=self.word_freq,
            font_path=font_path,
            background_color=bg_color,
            margin=margin,
            width=width, 
            height=height,
            max_font_size=font_max,
            min_font_size=font_min
        )

        output_path = os.path.join(gl.get_catch_dir(), "web_wordcloud.png")
        self.final_pic.to_file(output_path)
        
        try:
            with open(output_path, "rb") as f:
                img_data = f.read()
            stream = io.BytesIO(img_data)
            bmp = wx.Bitmap(wx.Image(stream, wx.BITMAP_TYPE_PNG))
            self.PicShow_Bitmap.SetBitmap(bmp)
        except Exception as e:
            print(f"显示图片失败: {e}")

        dlg = wx.MessageDialog(self, '生成成功！',
                               '处理结果!',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Save_ButtonOnButtonClick(self, event):
        if self.final_pic is None:
            dlg = wx.MessageDialog(self, '您尚未生成词云！',
                               '错误信息!',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        wildcard = "PNG图片 (*.png)|*.png|JPG图片 (*.jpg)|*.jpg|PDF文件 (*.pdf)|*.pdf|SVG文件 (*.svg)|*.svg"
        dlg = wx.FileDialog(
            self, message="保存单词云，请选择合适的格式", defaultDir=gl.CWD,
            defaultFile="MyWordCloud", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            exporter_inst = exporter.WordCloudExporter()
            exporter_inst.export_image(self.final_pic, path, dpi=300)

        dlg.Destroy()
        dlg = wx.MessageDialog(self, '保存完成！',
                               '处理结果!',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Export_ButtonOnButtonClick(self, event):
        if not self.word_freq:
            dlg = wx.MessageDialog(self, '请先生成词云！',
                               '提示',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
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
                
                dlg2 = wx.MessageDialog(self, f'报告已生成: {path}', '完成', wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
            except Exception as e:
                dlg2 = wx.MessageDialog(self, f'生成报告失败: {str(e)}', '错误', wx.OK | wx.ICON_ERROR)
                dlg2.ShowModal()
                dlg2.Destroy()
        
        dlg.Destroy()

    def GetConf(self):
        stop_word_file = self.stop_word_file
        goal_file = self.goal_file
        margin = self.Margin_spinCtrl.GetValue()
        width = self.Width_spinCtrl.GetValue()
        height = self.Height_spinCtrl.GetValue()
        font = self.Font_Choice.GetString(self.Font_Choice.GetCurrentSelection())
        font_max = self.MaxFont_spinCtrl.GetValue()
        font_min = self.MinFont_spinCtrl.GetValue()
        bg_color = self.BG_Color_colourPicker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        return stop_word_file, goal_file, margin, width, height, font, font_max, font_min, bg_color
    
    def update_Choice(self):
        fonts = gl.get_available_fonts()
        self.Font_Choice.Clear()
        if fonts:
            self.Font_Choice.AppendItems(fonts)
            self.Font_Choice.SetSelection(0)
        return fonts
