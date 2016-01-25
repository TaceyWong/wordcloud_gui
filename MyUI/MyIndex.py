# coding:utf-8


import wx
import wx.richtext
import xlwt
import os
import sys
import StringIO
from Utils import gl
from Core.specificwords_extract import *

###########################################################################
## 单词索引（Word Indexing）
###########################################################################

class MyIndex(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(587, 489),
                          style=wx.TAB_TRAVERSAL)

        self.index_result = ""
        self.index_word=""
        self.index_file=""

        self.doLayout()
        # Connect Events
        self.indexSearch.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.indexSearchOnCancelButton)
        self.indexSearch.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.indexSearchOnSearchButton)
        self.indexSearch.Bind(wx.EVT_TEXT, self.indexSearchOnText)
        self.indexSearch.Bind(wx.EVT_TEXT_ENTER, self.indexSearchOnTextEnter)
        self.open_Button.Bind(wx.EVT_BUTTON, self.open_ButtonOnButtonClick)
        self.save_txt_Button.Bind(wx.EVT_BUTTON, self.save_txt_ButtonOnButtonClick)
        self.save_html_Button.Bind(wx.EVT_BUTTON, self.save_html_ButtonOnButtonClick)
        self.save_xls_Button.Bind(wx.EVT_BUTTON, self.save_xls_ButtonOnButtonClick)

    def __del__(self):
        pass

    def initGlobalValue(self):
        self.inputPath = None


    def doLayout(self):
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        Index_Sizer = wx.BoxSizer(wx.VERTICAL)

        fgSizer1 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        open_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"第一步：请打开要检索的文档"), wx.HORIZONTAL)

        self.open_Button = wx.Button(open_sbSizer.GetStaticBox(), wx.ID_ANY, u"打开要检索的目标文档", wx.DefaultPosition,
                                     wx.DefaultSize,
                                     0)
        open_sbSizer.Add(self.open_Button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.info_file = wx.StaticText(open_sbSizer.GetStaticBox(), wx.ID_ANY, u"当前要检索的目标文档为：（空）请点击左边按钮进行选择",
                                       wx.DefaultPosition,
                                       wx.Size(530,-1), wx.ALL | wx.SUNKEN_BORDER | wx.ALIGN_CENTER_VERTICAL)#ALIGN_CENTER)
        self.info_file.Wrap(-1)
        self.info_file.Enable(False)

        open_sbSizer.Add(self.info_file, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        fgSizer1.Add(open_sbSizer, 1, wx.EXPAND, 5)

        self.statu_file = wx.StaticText(self, wx.ID_ANY, u"支持检索所打开的文档", wx.DefaultPosition, wx.DefaultSize,
                                        0 | wx.RAISED_BORDER)
        self.statu_file.Hide()
        self.statu_file.Wrap(-1)
        fgSizer1.Add(self.statu_file, 0, wx.ALL, 5)

        index_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"第二步：请输入要检索的词汇"), wx.VERTICAL)

        self.indexSearch = wx.SearchCtrl(index_sbSizer.GetStaticBox(), wx.ID_ANY, u"", wx.DefaultPosition,
                                         wx.Size(680, -1), 0)
        self.indexSearch.ShowSearchButton(True)
        self.indexSearch.ShowCancelButton(True)
        self.indexSearch.Disable()
        index_sbSizer.Add(self.indexSearch, 0, wx.ALL, 5)

        fgSizer1.Add(index_sbSizer, 1, wx.EXPAND, 5)

        self.statu_index = wx.StaticText(self, wx.ID_ANY, u"正在检索···", wx.DefaultPosition, wx.DefaultSize,
                                         0 | wx.RAISED_BORDER)
        self.statu_index.Hide()
        self.statu_index.Wrap(-1)

        fgSizer1.Add(self.statu_index, 0, wx.ALL, 5)

        result_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"检索结果"), wx.VERTICAL)

        self.m_richText2 = wx.richtext.RichTextCtrl(result_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                                    wx.DefaultPosition, wx.Size(660, 400),
                                                    wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.WANTS_CHARS)
        result_sbSizer.Add(self.m_richText2, 1, wx.EXPAND | wx.ALL, 5)

        fgSizer1.Add(result_sbSizer, 1, wx.EXPAND, 5)

        out_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"检索结果保存"), wx.VERTICAL)

        self.save_txt_Button = wx.Button(out_sbSizer.GetStaticBox(), wx.ID_ANY, u"将结果导出为TXT文本", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        out_sbSizer.Add(self.save_txt_Button, 0, wx.ALL, 5)

        self.save_html_Button = wx.Button(out_sbSizer.GetStaticBox(), wx.ID_ANY, u"将结果保存为HTM网页", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        out_sbSizer.Add(self.save_html_Button, 0, wx.ALL, 5)

        self.save_xls_Button = wx.Button(out_sbSizer.GetStaticBox(), wx.ID_ANY, u"将结果保存为XLS表格", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        out_sbSizer.Add(self.save_xls_Button, 0, wx.ALL, 5)

        fgSizer1.Add(out_sbSizer, 1, wx.EXPAND, 5)

        Index_Sizer.Add(fgSizer1, 1, wx.EXPAND, 5)

        self.SetSizer(Index_Sizer)
        self.Layout()


    # Virtual event handlers, overide them in your derived class
    def indexSearchOnCancelButton(self, event):
        event.Skip()
        print "cancel btn"

    def indexSearchOnSearchButton(self, event):
        event.Skip()

        self.index_file = self.info_file.GetLabelText()
        self.index_word= self.indexSearch.GetValue()
        origin = sys.stdout
        result = StringIO.StringIO()
        sys.stdout = result
        if len(self.index_word.strip().split(" ")) >1:
            dlg = wx.MessageDialog(self,u'请输入单个词汇！',
                                u'警告!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return 1

        self.statu_index.SetBackgroundColour(wx.YELLOW)
        self.statu_index.Show()
        self.indexSearch.Disable()
        indexTextUsingLancasterStemmer(self.index_file, self.index_word.strip())
        sys.stdout = origin
        self.index_result = result.getvalue()
        result.close()
        temp_out = self.index_result.split("\n")
        self.m_richText2.Clear()
        # self.m_richText2.BeginFontSize(14)
        # self.m_richText2.BeginAlignment(wx.TEXT_ALIGNMENT_CENTRE)
        # self.m_richText2.BeginBold()
        # self.m_richText2.WriteText("The Result of Indexing '%s' from %s"
        #                             % (self.index_word, self.index_file.split("\\")[-1]))
        # self.m_richText2.EndFontSize()
        # self.m_richText2.EndBold()
        # self.m_richText2.EndAlignment()
        self.m_richText2.Newline()

        if len(temp_out) <=0:
            self.m_richText2.BeginBold()
            self.m_richText2.WriteText(u"在该文档中未检索到"+self.index_word)
            self.m_richText2.EndBold()
        else:
            temp_out.pop()
            for id,i in enumerate(temp_out):

                self.m_richText2.WriteText(str(id)+": "+i[:41])
                self.m_richText2.BeginBold()
                self.m_richText2.WriteText(self.index_word)
                self.m_richText2.EndBold()
                self.m_richText2.WriteText(i[41+len(self.index_word):])
                self.m_richText2.Newline()

        self.statu_index.Hide()
        self.indexSearch.Enable()


    def indexSearchOnText(self, event):
        event.Skip()

        print "ontext"

    def indexSearchOnTextEnter(self, event):
        event.Skip()
        print "text enter"

    def open_ButtonOnButtonClick(self, event):
        event.Skip()
        wildcard = u"TXT纯文本 (*.txt)|*.txt|" \
                   u"HTML网页文本 (*.html)|*.html|" \
                   u"HTML网页文本 (*.htm)|*.htm"

        dlg = wx.FileDialog(
            self, message=u"选取一个要检索的文档",
            defaultDir=gl.CWD+"\\Data\\cleaned\\",
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR  # | wx.MULTIPLE
        )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()  # GetPaths()
            self.info_file.SetLabelText(path)
            self.info_file.Enable(True)
            self.statu_file.SetBackgroundColour(wx.GREEN)
            self.statu_file.Show()
            self.indexSearch.Enable()

        dlg.Destroy()


    def save_txt_ButtonOnButtonClick(self, event):
        event.Skip()
        dlg = wx.FileDialog(
            self, message=u"以TXT文本形式保存", defaultDir=os.getcwd(),
            defaultFile="", wildcard=u"TXT纯文本 (*.txt)|*.txt", style=wx.SAVE
        )

        # dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        else:
            return 0
        fp = file(path, 'w') # Create file anew
        fp.write(self.index_result)
        fp.close()
        dlg.Destroy()
        dlg = wx.MessageDialog(self,u'保存完成！',
                                u'处理结果!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()


    def save_html_ButtonOnButtonClick(self, event):
        event.Skip()
        temp_out = self.index_result.split("\n")
        html_style = '''
                    <html>
                        <title>Result</title>
                        <body>
                            <h1 style="text-align:center">The Result of Indexing %s from %s</h1>
                    ''' % (self.index_word,self.index_file.split("\\")[-1])
        for i in temp_out:
            html_style += '<pre><p style="text-align:center">' + str(i) + "</p></pre>"+"\n<hr>"
        html_style += """
                     </body>
                     </html>
                      """
        dlg = wx.FileDialog(
            self, message=u"以HTML网页形式保存", defaultDir=os.getcwd(),
            defaultFile="", wildcard=u"HTML网页格式保存 (*.html)|*.html", style=wx.SAVE
        )

        # dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        else:
            return 0
        fp = file(path, 'w') # Create file anew
        fp.write(html_style)
        fp.close()
        dlg.Destroy()
        dlg = wx.MessageDialog(self,u'处理结果！',
                                u'保存完成!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()


    def save_xls_ButtonOnButtonClick(self, event):
        event.Skip()
        dlg = wx.FileDialog(
            self, message=u"以Excel表格形式保存", defaultDir=os.getcwd(),
            defaultFile="", wildcard=u"Excel表格 (*.xls)|*.xls", style=wx.SAVE
        )

        # dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        else:
            return 0

        xls_file = xlwt.Workbook()
        xls_table = xls_file.add_sheet("Result")
        # xls_table = xls_file.add_sheet("Result",cell_overwrite_ok=True)
        xls_style = xlwt.XFStyle()
        temp_out = self.index_result.split("\n")
        for ID,value in enumerate(temp_out):
            xls_table.write(ID,0,ID,xls_style)
            xls_table.write(ID,1,value,xls_style)
        xls_file.save(path)

        dlg.Destroy()
        dlg = wx.MessageDialog(self,u'保存完成！',
                                u'处理结果!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()




