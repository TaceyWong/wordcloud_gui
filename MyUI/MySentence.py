#coding:utf-8



import wx
import wx.richtext
from Utils import gl
import os
import xlwt
###########################################################################
## Class MyPanel1
###########################################################################

class MySentence(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        self.content = None
        self.search_word = None
        self.select_curpos = None
        self.num_sentence = None
        self.radio_select = 0
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        search_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"检索设置"), wx.HORIZONTAL)

        self.corpus_staticText = wx.StaticText(search_sbSizer.GetStaticBox(), wx.ID_ANY, u"请选择要检索的库", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.corpus_staticText.Wrap(-1)
        search_sbSizer.Add(self.corpus_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        curpos_ChoiceChoices = []#self.updatecorpus()
        self.curpos_Choice = wx.Choice(search_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                   curpos_ChoiceChoices, 0)
        self.curpos_Choice.SetSelection(0)
        self.curpos_Choice.SetToolTipString(u"选择从哪一个中国特色词库中进行检索")

        search_sbSizer.Add(self.curpos_Choice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.sentence_num_staticText = wx.StaticText(search_sbSizer.GetStaticBox(), wx.ID_ANY, u"请选择要显示的例句个数", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.sentence_num_staticText.Wrap(-1)
        search_sbSizer.Add(self.sentence_num_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.sentence_num_spinCtrl = wx.SpinCtrl(search_sbSizer.GetStaticBox(), wx.ID_ANY, u"3", wx.DefaultPosition, wx.Size(80, -1),
                                       wx.SP_ARROW_KEYS, 0, 10, 3)
        self.sentence_num_spinCtrl.SetToolTipString(u"调节要显示的例句的个数")

        search_sbSizer.Add(self.sentence_num_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # self.m_staticText8 = wx.StaticText(search_sbSizer.GetStaticBox(), wx.ID_ANY, u"设置检索方式", wx.DefaultPosition,
        #                                    wx.DefaultSize, 0)
        # self.m_staticText8.Wrap(-1)
        # search_sbSizer.Add(self.m_staticText8, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # 
        # m_choice2Choices = [u"拼音", wx.EmptyString]
        # self.m_choice2 = wx.Choice(search_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
        #                            m_choice2Choices, 0)
        # self.m_choice2.SetSelection(0)
        # self.m_choice2.SetToolTipString(u"选择检索方式")
        # 
        # search_sbSizer.Add(self.m_choice2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer3.Add(search_sbSizer, 1, wx.EXPAND, 5)

        self.search_searchCtrl = wx.SearchCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(400, -1))
                                           #wx.TE_NOHIDESEL | wx.TAB_TRAVERSAL )#| wx.WANTS_CHARS)
        self.search_searchCtrl.ShowSearchButton(True)
        self.search_searchCtrl.ShowCancelButton(True)
        self.search_searchCtrl.SetToolTipString(u"请输入要检索的词汇")

        bSizer3.Add(self.search_searchCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        gbSizer1 = wx.GridBagSizer(0, 0)
        gbSizer1.SetFlexibleDirection(wx.BOTH)
        gbSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        export_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"检索结果导出"), wx.VERTICAL)

        export_radioBoxChoices = [u"导出当前搜索结果", u"导出当前库全部搜索结果"]
        self.export_radioBox = wx.RadioBox(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"选择要导出的数据", wx.DefaultPosition,
                                       wx.DefaultSize, export_radioBoxChoices, 1, wx.RA_SPECIFY_COLS)
        self.export_radioBox.SetSelection(0)
        self.export_radioBox.SetToolTipString(u"进行例句检索结果导出选取")

        export_sbSizer.Add(self.export_radioBox, 0, wx.ALL, 5)

        self.export_txt_Button = wx.Button(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出为TXT纯文本", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.export_txt_Button.SetToolTipString(u"将结果导出为TXT纯文本格式，可用一般记事本程序打开。")

        export_sbSizer.Add(self.export_txt_Button, 0, wx.ALL, 5)

        self.export_html_Button = wx.Button(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出为HTML网页", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.export_html_Button.SetToolTipString(u"将结果保存为HTML网页文件，样式较为丰富，可用浏览器程序打开浏览。")

        export_sbSizer.Add(self.export_html_Button, 0, wx.ALL, 5)

        self.export_excel_Button = wx.Button(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出为Excel表格", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.export_excel_Button.SetToolTipString(u"将结果保存为Excel表格文件，便于在Excel中进行处理分发，可用Office表格软件打开。")

        export_sbSizer.Add(self.export_excel_Button, 0, wx.ALL, 5)

        gbSizer1.Add(export_sbSizer, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND, 5)

        sbSizer8 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"当前搜索结果"), wx.VERTICAL)

        self.result_richText = wx.richtext.RichTextCtrl(sbSizer8.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                                    wx.DefaultPosition, wx.Size(660, 400),
                                                    wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.WANTS_CHARS)
        sbSizer8.Add(self.result_richText, 1, wx.EXPAND | wx.ALL, 5)

        gbSizer1.Add(sbSizer8, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.EXPAND, 5)

        bSizer3.Add(gbSizer1, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer3)
        self.Layout()

        # Connect Events
        self.curpos_Choice.Bind(wx.EVT_CHOICE, self.curpos_ChoiceOnChoice)
        self.sentence_num_spinCtrl.Bind(wx.EVT_SPINCTRL, self.sentence_num_spinCtrlOnSpinCtrl)
        self.sentence_num_spinCtrl.Bind(wx.EVT_TEXT, self.sentence_num_spinCtrlOnSpinCtrlText)
        self.sentence_num_spinCtrl.Bind(wx.EVT_TEXT_ENTER, self.sentence_num_spinCtrlOnTextEnter)
        self.search_searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.search_searchCtrlOnSearchButton)
        self.search_searchCtrl.Bind(wx.EVT_TEXT, self.search_searchCtrlOnText)
        self.search_searchCtrl.Bind(wx.EVT_TEXT_ENTER, self.search_searchCtrlOnTextEnter)
        self.export_radioBox.Bind(wx.EVT_RADIOBOX, self.export_radioBoxOnRadioBox)
        self.export_txt_Button.Bind(wx.EVT_BUTTON, self.export_txt_ButtonOnButtonClick)
        self.export_html_Button.Bind(wx.EVT_BUTTON, self.export_html_ButtonOnButtonClick)
        self.export_excel_Button.Bind(wx.EVT_BUTTON, self.export_excel_ButtonOnButtonClick)

    def __del__(self):
        pass


    # Virtual event handlers, overide them in your derived class
    def curpos_ChoiceOnChoice(self, event):
        event.Skip()

    def sentence_num_spinCtrlOnSpinCtrl(self, event):
        event.Skip()

    def sentence_num_spinCtrlOnSpinCtrlText(self, event):
        event.Skip()

    def sentence_num_spinCtrlOnTextEnter(self, event):
        event.Skip()

    def search_searchCtrlOnSearchButton(self, event):
        event.Skip()
        self.search_word=self.search_searchCtrl.GetValue()
        self.select_curpos = self.curpos_Choice.GetString(self.curpos_Choice.GetCurrentSelection())
        self.num_sentence = self.sentence_num_spinCtrl.GetValue()
        gl.DB_CURSOR.execute("show tables")
        tables = [tb[0] for tb in gl.DB_CURSOR.fetchall()]
        print tables
        try:
            self.select_curpos = self.select_curpos.lower()
        except:
            pass
        if self.select_curpos+"_sentence" not in tables:
            self.message(info1=u'您所选的词库尚未生成例句！',info2=u"警告")

            return 1
            # print u"您所选的词库尚未生成例句"

        else:
            # print "success"

            import MySQLdb
            try:
                n = gl.DB_CURSOR.execute("select * from %s_word where en_word = '%s'"%(self.select_curpos,self.search_word))
                if n<1:
                    self.message(info1=u'搜索的词在特色词库中不存在！',info2=u"警告")
                    return 1
                gl.DB_CURSOR.execute("select sent_content from %s_sentence where word_id = (select DISTINCT word_id from %s_word where en_word='%s')  limit %s"%(self.select_curpos,self.select_curpos,self.search_word,self.num_sentence))
                self.result_richText.Clear()
                self.content = gl.DB_CURSOR.fetchall()
                if len(self.content)<1:
                    self.result_richText.WriteText(u"无此特色词的例句")
                    return 0
                for id,sentence in enumerate(self.content):

                    # self.SetFontStyle(fontColor=wx.Colour(0, 0, 0), fontBgColor=wx.Colour(255, 255, 255), fontFace='Times New Roman', fontSize=14, fontBold=False, fontItalic=False, fontUnderline=False)
                    self.result_richText.BeginFontSize(16)
                    self.result_richText.BeginBold()
                    self.result_richText.WriteText(u"例句"+str(id+1)+u" :")
                    self.result_richText.EndBold()
                    self.result_richText.EndFontSize()
                    self.result_richText.Newline()
                    self.result_richText.BeginFontSize(14)
                    # self.result_richText.SetFontStyle(fontColor=wx.Colour(0, 0, 0),fontSize=14, fontBold=False)
                    self.result_richText.WriteText(u"   "+sentence[0])
                    self.result_richText.EndFontSize()
                    self.result_richText.Newline()
                    self.result_richText.Newline()

            except MySQLdb.Error,e:
                print "Mysql Error %d: %s" % (e.args[0], e.args[1])


    def updatecorpus(self):
        n = gl.DB_CURSOR.execute("select lib_name from curpos")
        curpos_ChoiceChoices = []
        if n>0:
            curpos_ChoiceChoices = [i[0] for i in gl.DB_CURSOR.fetchall()]
        else:
            curpos_ChoiceChoices = []
        self.curpos_Choice.Clear()
        self.curpos_Choice.AppendItems([i for i in curpos_ChoiceChoices])
        print "sentence update"
        return curpos_ChoiceChoices

    def search_searchCtrlOnText(self, event):
        event.Skip()

    def search_searchCtrlOnTextEnter(self, event):
        event.Skip()

    def export_radioBoxOnRadioBox(self, event):
        event.Skip()
        self.radio_select = event.GetInt()

    def export_txt_ButtonOnButtonClick(self, event):
        event.Skip()
        self.export(type="txt")
    def export_html_ButtonOnButtonClick(self, event):
        event.Skip()
        self.export(type="html")
    def export_excel_ButtonOnButtonClick(self, event):
        event.Skip()
        self.export(type="excel")

    def export(self,type=None):
        self.search_word = self.search_searchCtrl.GetValue()
        self.select_curpos = self.curpos_Choice.GetString(self.curpos_Choice.GetCurrentSelection())
        if self.radio_select ==1:
            if self.search_word =="":
                self.message(info1=u"搜索词为空，无法导出",info2=u"警告")
                return 0
            # self.select_curpos = self.curpos_Choice.GetString(self.curpos_Choice.GetCurrentSelection())

            n=gl.DB_CURSOR.execute("select sent_content from %s_sentence where word_id = (select DISTINCT word_id from %s_word where en_word='%s') "%(self.select_curpos,self.select_curpos,self.search_word))
            if n==0:
                self.message(info1=u"该词非特色词",info2=u"警告")
                return 0
            content = gl.DB_CURSOR.fetchall()
        else:
            if self.content ==None or len(self.content)<1:
                self.message(info1=u"例句结果为空",info2=u"警告")
                return 0
            content = self.content


        #以TXT文本保存
        if type == "txt":
            dlg = wx.FileDialog(
                     self, message=u"以TXT文本形式保存", defaultDir=os.getcwd(),
                    defaultFile="", wildcard=u"TXT纯文本 (*.txt)|*.txt", style=wx.SAVE
                    )

            # Show the dialog and retrieve the user response. If it is the OK response,
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
            else:
                return 0
            try:
                fp = file(path, 'w') # Create file anew
                fp.write(u"特色词【%s】的例句"%(self.search_word)+"\n\n")
                for ID,sentence in enumerate(content):
                    fp.write(u"例句"+str(ID+1)+" :"+sentence[0]+"\n\n")
                fp.close()
            except:
                pass
            dlg.Destroy()
            self.message(info1=u"保存完成",info2=u"处理结果")
            return 0
        #以HTML网页保存
        elif type == "html":
            dlg = wx.FileDialog(
                                self, message=u"以HTML网页形式保存", defaultDir=os.getcwd(),
                                defaultFile="", wildcard=u"HTML网页格式保存 (*.html)|*.html", style=wx.SAVE
                                )

            # Show the dialog and retrieve the user response. If it is the OK response,
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
            else:
                return 0
            html_style = '''
                    <!DOCTYPE html>
                    <html>
                    <head lang="en">
                        <meta charset="UTF-8">
                        <title>Result</title>
                        <body>
                            <h1 style="text-align:center">特色词%s的例句</h1>
                    ''' % (self.search_word)
            for ID,sentence in enumerate(content):
                # html_style += '<pre><p style="text-align:center">' +u"例句" +str(ID+1) +" :"+ sentence[0]+"</p></pre>"+"\n<hr>"
                html_style += '<pre><p >' +u"例句" +str(ID+1) +" :"+ sentence[0]+"</p></pre>"+"\n<hr>"
            html_style += """
                                    </body>
                                </html>
                            """

            try:
                fp = file(path, 'w') # Create file anew
                fp.write(html_style)
                fp.close()
            except:
                pass
            dlg.Destroy()
            self.message(info1=u"保存完成",info2=u"处理结果")
            return 0

        #以EXCEL表格保存
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
        for ID,value in enumerate(content):
            xls_table.write(ID,0,ID+1,xls_style)
            xls_table.write(ID,1,value,xls_style)
        xls_file.save(path)

        dlg.Destroy()
        self.message(info1=u"保存完成",info2=u"处理结果")
        dlg.Destroy()

    def message(self,info1=None,info2=None):
        dlg = wx.MessageDialog(self,u'%s！'%info1,
                                u'%s!'%info2,
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()


