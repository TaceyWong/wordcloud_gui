# coding:utf-8

import wx
from Utils import gl

__author__ = 'Tacey Wong'


###########################################################################
## 文本抽取生成词云
###########################################################################

class MyText(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"词云配置"), wx.HORIZONTAL)

        sbSizer4 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, u"目标文件"), wx.VERTICAL)

        fgSizer4 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.StopWords_Button = wx.Button(sbSizer4.GetStaticBox(), wx.ID_ANY, u"打开停词表", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer4.Add(self.StopWords_Button, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText10 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"当前：无", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_staticText10.Wrap(-1)
        self.m_staticText10.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

        fgSizer4.Add(self.m_staticText10, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.GoalFile_Button = wx.Button(sbSizer4.GetStaticBox(), wx.ID_ANY, u"打开目标文件", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer4.Add(self.GoalFile_Button, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText11 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"当前：无", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_staticText11.Wrap(-1)
        self.m_staticText11.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

        fgSizer4.Add(self.m_staticText11, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sbSizer4.Add(fgSizer4, 1, wx.EXPAND, 5)

        sbSizer1.Add(sbSizer4, 1, wx.EXPAND, 5)

        sbSizer5 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, u"尺寸设置"), wx.VERTICAL)

        fgSizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer2.SetFlexibleDirection(wx.BOTH)
        fgSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText1 = wx.StaticText(sbSizer5.GetStaticBox(), wx.ID_ANY, u"边距", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        fgSizer2.Add(self.m_staticText1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spinCtrl1 = wx.SpinCtrl(sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.SP_ARROW_KEYS, 0, -1, 0)
        fgSizer2.Add(self.m_spinCtrl1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText2 = wx.StaticText(sbSizer5.GetStaticBox(), wx.ID_ANY, u"宽度", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        fgSizer2.Add(self.m_staticText2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spinCtrl2 = wx.SpinCtrl(sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.SP_ARROW_KEYS, 100, 10000, 800)
        fgSizer2.Add(self.m_spinCtrl2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText3 = wx.StaticText(sbSizer5.GetStaticBox(), wx.ID_ANY, u"高度", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        fgSizer2.Add(self.m_staticText3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spinCtrl3 = wx.SpinCtrl(sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.SP_ARROW_KEYS, 80, 10000, 600)
        fgSizer2.Add(self.m_spinCtrl3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sbSizer5.Add(fgSizer2, 1, wx.EXPAND, 5)

        sbSizer1.Add(sbSizer5, 1, wx.EXPAND, 5)

        sbSizer6 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, u"字体设置"), wx.VERTICAL)

        fgSizer3 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer3.SetFlexibleDirection(wx.BOTH)
        fgSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText4 = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, u"选择字体", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        fgSizer3.Add(self.m_staticText4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.m_fontPicker2 = wx.FontPickerCtrl(sbSizer6.GetStaticBox(), wx.ID_ANY, wx.NullFont, wx.DefaultPosition,
                                               wx.DefaultSize, wx.FNTP_DEFAULT_STYLE)
        self.m_fontPicker2.SetMaxPointSize(100)
        fgSizer3.Add(self.m_fontPicker2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText5 = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, u"最大字体", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)
        fgSizer3.Add(self.m_staticText5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.m_spinCtrl4 = wx.SpinCtrl(sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 40, 10)
        fgSizer3.Add(self.m_spinCtrl4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText6 = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, u"最小字体", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)
        fgSizer3.Add(self.m_staticText6, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.m_spinCtrl5 = wx.SpinCtrl(sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 40, 5)
        fgSizer3.Add(self.m_spinCtrl5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sbSizer6.Add(fgSizer3, 1, wx.EXPAND, 5)

        sbSizer1.Add(sbSizer6, 1, wx.EXPAND, 5)

        sbSizer7 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, u"颜色设置"), wx.VERTICAL)

        self.m_staticText8 = wx.StaticText(sbSizer7.GetStaticBox(), wx.ID_ANY, u"选择背景颜色", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText8.Wrap(-1)
        sbSizer7.Add(self.m_staticText8, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_colourPicker1 = wx.ColourPickerCtrl(sbSizer7.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition,
                                                   wx.DefaultSize, wx.CLRP_DEFAULT_STYLE)
        sbSizer7.Add(self.m_colourPicker1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        sbSizer1.Add(sbSizer7, 1, wx.EXPAND, 5)

        bSizer1.Add(sbSizer1, 1, wx.EXPAND, 5)

        sbSizer3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"词云生成"), wx.VERTICAL)

        fgSizer1 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_button1 = wx.Button(sbSizer3.GetStaticBox(), wx.ID_ANY, u"词云生成", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button3 = wx.Button(sbSizer3.GetStaticBox(), wx.ID_ANY, u"保存词云", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.m_button3, 0, wx.ALL, 5)

        fgSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        sbSizer9 = wx.StaticBoxSizer(wx.StaticBox(sbSizer3.GetStaticBox(), wx.ID_ANY, u"词云预览"), wx.VERTICAL)

        self.m_bitmap2 = wx.StaticBitmap(sbSizer9.GetStaticBox(), wx.ID_ANY,
                                         wx.Bitmap(u"C:\\Users\\Administrator\\Desktop\\论文资料\\test.png",
                                                   wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer9.Add(self.m_bitmap2, 1, wx.ALL | wx.EXPAND, 5)

        fgSizer1.Add(sbSizer9, 1, wx.EXPAND, 5)

        sbSizer3.Add(fgSizer1, 1, wx.EXPAND, 5)

        bSizer1.Add(sbSizer3, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        # Connect Events
        self.StopWords_Button.Bind(wx.EVT_BUTTON, self.StopWords_ButtonOnButtonClick)
        self.GoalFile_Button.Bind(wx.EVT_BUTTON, self.GoalFile_ButtonOnButtonClick)
        self.m_button1.Bind(wx.EVT_BUTTON, self.m_button1OnButtonClick)
        self.m_button3.Bind(wx.EVT_BUTTON, self.m_button3OnButtonClick)

    def __del__(self):
        pass


    # Virtual event handlers, overide them in your derived class
    def StopWords_ButtonOnButtonClick(self, event):
        event.Skip()
        wildcard = u"TXT纯文本 (*.txt)|*.txt"

        dlg = wx.FileDialog(
            self, message=u"选取停词表文档",
            defaultDir=gl.CWD,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR  # | wx.MULTIPLE
        )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()  # GetPaths()
        #
        dlg.Destroy()



    def GoalFile_ButtonOnButtonClick(self, event):
        event.Skip()
        wildcard = u"TXT纯文本 (*.txt)|*.txt"

        dlg = wx.FileDialog(
            self, message=u"选取词云生成目标文档",
            defaultDir=gl.CWD,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR  # | wx.MULTIPLE
        )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()  # GetPaths()
        #
        dlg.Destroy()


    def m_button1OnButtonClick(self, event):
        event.Skip()

    def m_button3OnButtonClick(self, event):
        event.Skip()



