# -*- coding: utf-8 -*-


import wx
import wx.grid
from Core.specificwords_extract import *
from Utils import gl
from Utils import DB
import chardet
import xlwt
import MySQLdb


###########################################################################
## 特色词提取与例句生成
###########################################################################

class MyGrid(wx.grid.Grid):
    def __init__(self, parent=None, ID=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.Size(620, 290), un=0):

        wx.grid.Grid.__init__(self, parent, -1,pos,size,un)
        self.collabel = [u"特色词英文",u"特色评分",u"特色词中文",u"最后更新时间"]
        self.parent= parent
        self.data = None
        self.current_page = 1
        self.total_pages = None
        self.lib_name = None
        self.init()
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClicked)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnGridCellChange )

    def init(self):

        self.CreateGrid(12, 4)
        self.EnableEditing(True)
        self.EnableGridLines(True)
        self.SetGridLineColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        self.EnableDragGridSize(False)
        self.SetMargins(0, 0)

        # Columns
        self.EnableDragColMove(False)
        self.EnableDragColSize(True)
        # self.data_Grid.SetColLabelSize(30)
        self.SetColSize(0,190)
        self.SetColSize(1,60)
        self.SetColSize(2,140)
        self.SetColSize(3,150)
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetColAttr(3, attr)
        self.SetColAttr(1, attr)

        self.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.EnableDragRowSize(True)
        self.SetRowLabelSize(70)
        self.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        for i,v in enumerate(self.collabel):
            print i,v
            self.SetColLabelValue(i, v)

        #
        for i in range(1,12):
            self.SetRowLabelValue(i,str(i+1))
                # Grid

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        pass

    def update(self):
        self.ClearGrid()
        # for i,v in enumerate(self.collabel):
        #     print i,v
        #     self.SetColLabelValue(i, v)
        #
        # #
        print self.current_page
        try:
            for id ,values in enumerate(self.data[12*(self.current_page-1):12*self.current_page]):
                for i in range(len(values)):self.SetCellValue(id,i,str(values[i]).decode('utf-8').encode('gbk'))
                # self.SetCellValue(id,0,str(values[0]))
                # self.SetCellValue(id,1,str(values[1]))
                # self.SetCellValue(id,2,u"中文")#Why does this work？
                # print chardet.detect(str(values[2]))#why output "ascii",Fuck
                # print chardet.detect(str(values[2]).decode("ascii").encode("utf-8")) #Fuck
                # print chardet.detect(str(values[2]).decode("gb2312").encode("utf-8")) #Fuck
                # print chardet.detect(str(values[2]).decode("utf-8").encode("utf-8")) #Fuck
                # print chardet.detect(str(values[2]).decode("gbk").encode("utf-8")) #Fuck
                #Fuck the bitch-authors of MySQLdb & MySQL & GBK
                # self.SetCellValue(id,2,str(values[2]).decode('utf-8').encode('gbk'))#FUCK WORKING
                # self.SetCellValue(id,3,str(values[3]))
        except Exception,e:
            print e


        for id,value in enumerate(range(12*(self.current_page-1),12*self.current_page)):
            if value < len(self.data):
                self.SetRowLabelValue(id,str(value+1))



    def nextpage(self):
        self.current_page += 1
        self.update()

    def pripage(self):
        self.current_page -= 1
        self.update()

    def OnGridCellChange(self, evt):
        row, col = evt.GetRow(), evt.GetCol()
        # self.GetCell
        # self.SetCellValue(row,col)

    def OnLabelRightClicked(self, evt):

        # Did we click on a row or a column?
        row, col = evt.GetRow(), evt.GetCol()
        print row,col
        if col == -1: self.rowPopup(row, evt)

    def rowPopup(self, row, evt):
        """(row, evt) -> display a popup menu when a row label is right clicked"""
        modifyID = wx.NewId()
        appendID = wx.NewId()
        deleteID = wx.NewId()
        x = self.GetRowSize(row)/2

        if not self.GetSelectedRows():
            self.SelectRow(row)

        menu = wx.Menu()
        xo, yo = evt.GetPosition()
        menu.Append(modifyID,u"保存本行的修改")
        # menu.Append(appendID, u"增加一行")
        menu.Append(deleteID, u"确定删除本行")

        def modify(event,self=self,row=row):
            print u"修改本行"
            # row = self.GetSelectedRows()[0]
            en_word_old = self.data[(self.current_page-1)*12+row][0]
            en_word = self.GetCellValue(row,0)
            cn_word = self.GetCellValue(row,2)
            print en_word_old,en_word,cn_word
            try:
                gl.DB_CURSOR.execute("update %s_word set en_word='%s',cn_word='%s',time_last=now() where en_word='%s'"%(str(self.lib_name),str(en_word),str(cn_word),str(en_word_old)))
                gl.DB_CONN.commit()
            except Exception,e:
                print e
            self.data[(self.current_page-1)*12+row][0]=en_word
            # self.data[(self.current_page-1)*12+row][1]=str(10.00)
            self.data[(self.current_page-1)*12+row][2]=cn_word
            print self.data[(self.current_page-1)*12+row][2]
            self.data[(self.current_page-1)*12+row][3]=gl.TIME_NOW
            self.update()
            # self.Reset()

        def append(event, self=self, row=row):
            print u"追加一行"
            # self._table.AppendRow(row)
            # self.Reset()

        def delete(event, self=self, row=row):
            print u"删除本行"
            # row = self.GetSelectedRows()[0]
            try:
                en_word_old = self.data[(self.current_page-1)*12+row][0]

                gl.DB_CURSOR.execute("delete from %s_word where en_word='%s';"%(str(self.lib_name),str(en_word_old)))
                gl.DB_CONN.commit()
            except Exception,e:
                print e
            try:
                del self.data[(self.current_page-1)*12+row]
            except Exception ,e:
                print e
            self.update()
            # self._table.DeleteRows(rows)
            # self.Reset()
        self.Bind(wx.EVT_MENU, modify, id=modifyID)
        self.Bind(wx.EVT_MENU, append, id=appendID)
        self.Bind(wx.EVT_MENU, delete, id=deleteID)
        self.PopupMenu(menu)
        menu.Destroy()
        return














class MyExtract(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        self.curpos =None
        self.word_lib = None
        self.radio_select = None
        # self.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        extract_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"提取操作"), wx.VERTICAL)

        word_extract_sbSizer = wx.StaticBoxSizer(wx.StaticBox(extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"特色词提取"),
                                                 wx.VERTICAL)

        gSizer1 = wx.GridSizer(0, 2, 0, 0)

        self.corpus_staticText = wx.StaticText(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"请选择语料库",
                                               wx.DefaultPosition,
                                               wx.DefaultSize, 0)
        self.corpus_staticText.Wrap(-1)
        gSizer1.Add(self.corpus_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)


        corpus_ChoiceChoices=[]#self.update_corpus_Choice()

        self.corpus_Choice = wx.Choice(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                       wx.Size(100, -1),
                                       corpus_ChoiceChoices, 0)
        self.update_corpus_Choice()
        self.corpus_Choice.SetSelection(0)
        self.corpus_Choice.SetToolTipString(u"请选择一个已经清洗过的语料库")

        gSizer1.Add(self.corpus_Choice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.min_char_staticText = wx.StaticText(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"最小字符长度",
                                                 wx.DefaultPosition,
                                                 wx.DefaultSize, 0)
        self.min_char_staticText.Wrap(-1)
        gSizer1.Add(self.min_char_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.min_char_m_spinCtrl = wx.SpinCtrl(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                               wx.DefaultPosition,
                                               wx.Size(100, -1), wx.SP_ARROW_KEYS, 1, 3, 0)
        self.min_char_m_spinCtrl.SetToolTipString(u"请调节要提取的最小字符长度")

        gSizer1.Add(self.min_char_m_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.max_word_staticText = wx.StaticText(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"最大单词数",
                                                 wx.DefaultPosition,
                                                 wx.DefaultSize, 0)
        self.max_word_staticText.Wrap(-1)
        gSizer1.Add(self.max_word_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.max_word_spinCtrl = wx.SpinCtrl(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                             wx.DefaultPosition,
                                             wx.Size(100, -1), wx.SP_ARROW_KEYS, 2, 8, 5)
        self.max_word_spinCtrl.SetToolTipString(u"请调节要提取的最大单词个数")

        gSizer1.Add(self.max_word_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.min_frequency_staticText = wx.StaticText(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"最小关键字频率",
                                                      wx.DefaultPosition,
                                                      wx.DefaultSize, 0)
        self.min_frequency_staticText.Wrap(-1)
        gSizer1.Add(self.min_frequency_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.min_frequency_spinCtr = wx.SpinCtrl(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                                 wx.DefaultPosition,
                                                 wx.Size(100, -1), wx.SP_ARROW_KEYS, 1, 5, 2)
        self.min_frequency_spinCtr.SetToolTipString(u"请调节最小关键字频率")

        gSizer1.Add(self.min_frequency_spinCtr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.top_n_staticText = wx.StaticText(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"Top-N 特色词",
                                              wx.DefaultPosition,
                                              wx.DefaultSize, 0)
        self.top_n_staticText.Wrap(-1)
        gSizer1.Add(self.top_n_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.top_n_spinCtrl = wx.SpinCtrl(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                          wx.DefaultPosition,
                                          wx.Size(100, -1), wx.SP_ARROW_KEYS, 100, 3000, 101)
        self.top_n_spinCtrl.SetToolTipString(u"请调节Top-N 关键字个数")

        gSizer1.Add(self.top_n_spinCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.corpus_name_staticText = wx.StaticText(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"请给词库命名",
                                                    wx.DefaultPosition,
                                                    wx.DefaultSize, 0)
        self.corpus_name_staticText.Wrap(-1)
        gSizer1.Add(self.corpus_name_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.corpus_name_textCtrl = wx.TextCtrl(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                                wx.DefaultPosition,
                                                wx.Size(100, -1), 0)
        self.corpus_name_textCtrl.SetToolTipString(u"请给本次提取的特色词库命名")

        gSizer1.Add(self.corpus_name_textCtrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        word_extract_sbSizer.Add(gSizer1, 1, wx.EXPAND, 5)

        self.word_extract_Button = wx.Button(word_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"开始提取",
                                             wx.DefaultPosition, wx.DefaultSize, 0)
        self.word_extract_Button.SetToolTipString(u"开始从选定的语料库中进行特色词的提取")

        word_extract_sbSizer.Add(self.word_extract_Button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        extract_sbSizer.Add(word_extract_sbSizer, 1, wx.EXPAND, 5)

        sentence_extract_sbSizer = wx.StaticBoxSizer(wx.StaticBox(extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"例句生成"),
                                                     wx.VERTICAL)

        self.sentence_extract_m_staticText = wx.StaticText(sentence_extract_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                           u"特色词例句生成", wx.DefaultPosition,
                                                           wx.DefaultSize, 0)
        self.sentence_extract_m_staticText.Wrap(-1)
        sentence_extract_sbSizer.Add(self.sentence_extract_m_staticText, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.sentence_extract_Button = wx.Button(sentence_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"开始生成",
                                                 wx.DefaultPosition, wx.DefaultSize, 0)
        self.sentence_extract_Button.SetToolTipString(u"为已经提取的特色词词库生成例句")
        self.sentence_extract_Button.Disable()
        sentence_extract_sbSizer.Add(self.sentence_extract_Button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.sentence_extract_statu = wx.StaticText(sentence_extract_sbSizer.GetStaticBox(), wx.ID_ANY, u"请先提取词库",
                                                    wx.DefaultPosition,
                                                    wx.DefaultSize, 0)
        self.sentence_extract_statu.Wrap(-1)

        sentence_extract_sbSizer.Add(self.sentence_extract_statu, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        extract_sbSizer.Add(sentence_extract_sbSizer, 1, wx.EXPAND, 5)

        bSizer1.Add(extract_sbSizer, 1, wx.EXPAND, 5)

        edit_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"特色词查看和人工编辑"), wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.corpus_2_staticText = wx.StaticText(edit_sbSizer.GetStaticBox(), wx.ID_ANY, u"选择词库", wx.DefaultPosition,
                                                 wx.DefaultSize, wx.ALIGN_CENTRE)
        self.corpus_2_staticText.Wrap(-1)

        bSizer2.Add(self.corpus_2_staticText, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        corpus_choice2_ChoiceChoices = self.update_corpus_choice2_Choice()

        self.corpus_choice2_Choice = wx.Choice(edit_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                               wx.DefaultSize,
                                               corpus_choice2_ChoiceChoices, 0)
        self.corpus_choice2_Choice.SetSelection(0)
        self.corpus_choice2_Choice.SetToolTipString(u"选择一个要查看/编辑的特色词词库")

        bSizer2.Add(self.corpus_choice2_Choice, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.up_Button = wx.Button(edit_sbSizer.GetStaticBox(), wx.ID_ANY, u"上一页", wx.DefaultPosition, wx.DefaultSize,
                                   0)
        self.up_Button.SetToolTipString(u"显示上一页")
        self.up_Button.Disable()

        bSizer2.Add(self.up_Button, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.page_staticText = wx.StaticText(edit_sbSizer.GetStaticBox(), wx.ID_ANY, u"[第0页/共0页]", wx.DefaultPosition,
                                             wx.DefaultSize, wx.ALIGN_CENTRE)
        self.page_staticText.Wrap(-1)
        bSizer2.Add(self.page_staticText, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.down_Button = wx.Button(edit_sbSizer.GetStaticBox(), wx.ID_ANY, u"下一页", wx.DefaultPosition, wx.DefaultSize,
                                     0)
        self.down_Button.SetToolTipString(u"显示下一页")
        self.down_Button.Disable()
        bSizer2.Add(self.down_Button, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        edit_sbSizer.Add(bSizer2, 1, wx.EXPAND, 5)

        self.data_sbSizer = wx.StaticBoxSizer(wx.StaticBox(edit_sbSizer.GetStaticBox(), wx.ID_ANY, u"当前词库信息"),
                                         wx.VERTICAL)

        self.data_Grid = MyGrid(parent=self.data_sbSizer.GetStaticBox(), ID=wx.ID_ANY, pos=wx.DefaultPosition,size= wx.Size(620, 290), un=0)


        self.data_sbSizer.Add(self.data_Grid, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        edit_sbSizer.Add(self.data_sbSizer, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 5)

        export_sbSizer = wx.StaticBoxSizer(wx.StaticBox(edit_sbSizer.GetStaticBox(), wx.ID_ANY, u"词库导出"), wx.HORIZONTAL)

        export_radioBoxChoices = [u"导出当前词库", u"导出全部词库"]

        self.export_radioBox = wx.RadioBox(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出选择", wx.DefaultPosition,
                                           wx.DefaultSize,
                                           export_radioBoxChoices, 0, wx.RA_SPECIFY_COLS)
        self.export_radioBox.SetSelection(0)
        self.radio_select = 0
        self.export_radioBox.SetToolTipString(u"选择要导出的词库")

        export_sbSizer.Add(self.export_radioBox, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.export_txt_Button = wx.Button(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出TXT", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.export_txt_Button.SetToolTipString(u"导出为TXT纯文本，可用一般的记事本程序打开")

        export_sbSizer.Add(self.export_txt_Button, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.export_html_Button = wx.Button(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出HTML", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.export_html_Button.SetToolTipString(u"导出为HTML网页，可用浏览器程序打开")

        export_sbSizer.Add(self.export_html_Button, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.export_excel_Button = wx.Button(export_sbSizer.GetStaticBox(), wx.ID_ANY, u"导出EXCEL", wx.DefaultPosition,
                                             wx.DefaultSize,
                                             0)
        self.export_excel_Button.SetToolTipString(u"导出EXCEL表格文件，可用Office表格程序打开")

        export_sbSizer.Add(self.export_excel_Button, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        edit_sbSizer.Add(export_sbSizer, 1, wx.EXPAND, 5)

        bSizer1.Add(edit_sbSizer, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        # Connect Events
        self.corpus_Choice.Bind(wx.EVT_CHOICE, self.corpus_ChoiceOnChoice)
        self.min_char_m_spinCtrl.Bind(wx.EVT_SPINCTRL, self.min_char_m_spinCtrlOnSpinCtrl)
        self.min_char_m_spinCtrl.Bind(wx.EVT_TEXT, self.min_char_m_spinCtrlOnSpinCtrlText)
        self.max_word_spinCtrl.Bind(wx.EVT_SPINCTRL, self.max_word_spinCtrlOnSpinCtrl)
        self.max_word_spinCtrl.Bind(wx.EVT_TEXT, self.max_word_spinCtrlOnSpinCtrlText)
        self.min_frequency_spinCtr.Bind(wx.EVT_SPINCTRL, self.min_frequency_spinCtrOnSpinCtrl)
        self.min_frequency_spinCtr.Bind(wx.EVT_TEXT, self.min_frequency_spinCtrOnSpinCtrlText)
        self.top_n_spinCtrl.Bind(wx.EVT_SPINCTRL, self.top_n_spinCtrlOnSpinCtrl)
        self.top_n_spinCtrl.Bind(wx.EVT_TEXT, self.top_n_spinCtrlOnSpinCtrlText)
        self.word_extract_Button.Bind(wx.EVT_BUTTON, self.word_extract_ButtonOnButtonClick)
        self.sentence_extract_Button.Bind(wx.EVT_BUTTON, self.sentence_extract_ButtonOnButtonClick)
        self.corpus_choice2_Choice.Bind(wx.EVT_CHOICE, self.corpus_choice2_ChoiceOnChoice)
        self.up_Button.Bind(wx.EVT_BUTTON, self.up_ButtonOnButtonClick)
        self.down_Button.Bind(wx.EVT_BUTTON, self.down_ButtonOnButtonClick)
        self.export_radioBox.Bind(wx.EVT_RADIOBOX, self.export_radioBoxOnRadioBox)
        self.export_txt_Button.Bind(wx.EVT_BUTTON, self.export_txt_ButtonOnButtonClick)
        self.export_html_Button.Bind(wx.EVT_BUTTON, self.export_html_ButtonOnButtonClick)
        self.export_excel_Button.Bind(wx.EVT_BUTTON, self.export_excel_ButtonOnButtonClick)

    def __del__(self):
        pass


    # Virtual event handlers, overide them in your derived class
    def corpus_ChoiceOnChoice(self, event):
        event.Skip()
        # folder_list = os.listdir(os.getcwd()+"\\Data\\cleaned")
        # corpus_ChoiceChoices=[]
        # for i in folder_list:
        #     if os.path.isdir(os.getcwd()+"\\Data\\cleaned\\"+i):
        #         corpus_ChoiceChoices.append(i)
        # self.corpus_Choice.Clear()
        # self.corpus_Choice.AddChild(corpus_ChoiceChoices)

    def min_char_m_spinCtrlOnSpinCtrl(self, event):
        event.Skip()

    def min_char_m_spinCtrlOnSpinCtrlText(self, event):
        event.Skip()

    def max_word_spinCtrlOnSpinCtrl(self, event):
        event.Skip()

    def max_word_spinCtrlOnSpinCtrlText(self, event):
        event.Skip()

    def min_frequency_spinCtrOnSpinCtrl(self, event):
        event.Skip()

    def min_frequency_spinCtrOnSpinCtrlText(self, event):
        event.Skip()

    def top_n_spinCtrlOnSpinCtrl(self, event):
        event.Skip()

    def top_n_spinCtrlOnSpinCtrlText(self, event):
        event.Skip()

    def word_extract_ButtonOnButtonClick(self, event):
        event.Skip()
        if self.corpus_Choice.GetCurrentSelection()==-1:
            dlg = wx.MessageDialog(self,u'请先选择清洗后的语料库！！',
                                u'操作错误!',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        current_lib_name = self.corpus_name_textCtrl.GetValue()
        if current_lib_name=="":
            dlg = wx.MessageDialog(self,u'请先给本次提取的词库命名！！',
                                u'操作错误!',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        n = gl.DB_CURSOR.execute("select lib_name from curpos where lib_name='%s'"%current_lib_name)
        if n>0:
            dlg = wx.MessageDialog(self,u'该词库已存在，继续将删除原来的词库，是否继续！！',
                                u'操作错误!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return 0
        stopword_file = gl.CWD+"\\Data\\stopword\\Stopwordlist.txt"
        input_files_path =gl.CWD+"\\Data\\cleaned\\"+ self.corpus_Choice.GetString(self.corpus_Choice.GetCurrentSelection())+"\\"
        lib_name = self.corpus_name_textCtrl.GetValue()
        min_char_length = self.min_char_m_spinCtrl.GetValue()
        max_words_length= self.max_word_spinCtrl.GetValue()
        min_keyword_frequency = self.min_frequency_spinCtr.GetValue()
        topn_keywords = self.top_n_spinCtrl.GetValue()
        self.word_extract_Button.SetLabelText(u"正在提取···")
        self.word_extract_Button.Disable()
        try:
            result = extrac_keywords_docs(stopword_file,input_files_path,min_char_length, max_words_length,
                    min_keyword_frequency,topn_keywords)
        except Exception ,e:
            dlg = wx.MessageDialog(self,u'有进程占用文件夹，请关闭后重试！',
                                u'警告!',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            # print e
            return 1
        print result
        self.word_extract_Button.SetLabelText(u"正存入数据库")
        # params = [("%s"%lib_name,"%s"%i,score,gl.TIME_NOW) for i,score in result]
        # for i in params:
        #     print i
        # sql = "insert into words (id,lib_name,en_word,score,time_last) VALUES (uuid(),%s,%s,%s,%s)"
        # gl.DB_CURSOR.executemany(sql,params)
        # gl.DB_CONN.commit()
        # gl.DB_CURSOR.execute("insert into curpos VALUES('%s')"%lib_name)
        # gl.DB_CONN.commit()
        try:
            
            sql = ('DROP TABLE IF EXISTS ' + lib_name+'_word')
            gl.DB_CURSOR.execute(sql)
            gl.DB_CONN.commit()
            sql = ('DROP TABLE IF EXISTS ' + lib_name+'_sentence')
            gl.DB_CURSOR.execute(sql)
            gl.DB_CONN.commit()
            sql = "CREATE TABLE "+lib_name+"_word"+" (word_id  varchar(64) NOT NULL ,en_word  varchar(60) NOT NULL ,cn_word  varchar(60) NULL ,score  double(12,4) NULL ,time_last  datetime NULL ,PRIMARY KEY (word_id))charset='utf8';"
            gl.DB_CURSOR.execute(sql)
            gl.DB_CONN.commit()
            params = [("%s"%i,score,gl.TIME_NOW) for i,score in result]
            for i in params:
                print i
            sql = "insert into "+ lib_name+"_word (word_id,en_word,score,time_last) VALUES (uuid(),%s,%s,%s)"
            gl.DB_CURSOR.executemany(sql,params)
            gl.DB_CONN.commit()
            gl.DB_CURSOR.execute("insert into curpos VALUES('%s')"%lib_name)
            gl.DB_CONN.commit()

        except MySQLdb.Error,e:
            pass
            # print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        n = gl.DB_CURSOR.execute("select * from curpos")
        if n>0:
            self.corpus_choice2_Choice.Clear()
            self.corpus_choice2_Choice.AppendItems([i[0] for i in gl.DB_CURSOR.fetchall()])


        self.word_extract_Button.Enable()
        self.word_extract_Button.SetLabelText(u"开始提取")
        dlg = wx.MessageDialog(self,u'恭喜！特色词已经提取完成！！',
                                u'提取完成!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
        self.curpos =input_files_path
        self.word_lib = lib_name
        self.sentence_extract_Button.Enable()
        self.sentence_extract_statu.SetLabelText(u"可以开始生成例句")
        self.update_corpus_choice2_Choice()

    def sentence_extract_ButtonOnButtonClick(self, event):
        event.Skip()
        self.sentence_extract_Button.Disable()
        import MySQLdb
        # gl.DB_CURSOR.execute("select lib_name from curpos where lib_name='%s'"%self.word_lib)
        gl.DB_CURSOR.execute("select word_id,en_word from %s_word"%self.word_lib)
        words=gl.DB_CURSOR.fetchall()
        files = os.listdir(self.curpos)

        try:
            sql = ('DROP TABLE IF EXISTS ' + self.word_lib+'_sentence')
            gl.DB_CURSOR.execute(sql)
            gl.DB_CONN.commit()
            sql = "CREATE TABLE "+self.word_lib+"_sentence"+" (sent_id  varchar(64) NOT NULL ,word_id  varchar(64) NOT NULL ,sent_content  varchar(1024) NULL  ,time_last  datetime NULL ,PRIMARY KEY (sent_id))charset='utf8';"
            gl.DB_CURSOR.execute(sql)
            gl.DB_CONN.commit()

        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            return 1


        print files
        for word_id,en_word in words:
             sentences=[]
             for file in files:
                print word_id, en_word,file
                illus_sent = extracting_illustration(self.curpos+file,en_word)
                for i in illus_sent:
                    sentences.append(i[1])

             try:
                params = [("%s"%word_id,sentence,gl.TIME_NOW) for sentence in sentences ]
                sql = "insert into "+ self.word_lib+"_sentence (sent_id,word_id,sent_content,time_last) VALUES (uuid(),%s,%s,%s)"
                gl.DB_CURSOR.executemany(sql,params)
                gl.DB_CONN.commit()
             except MySQLdb.Error,e:
                print "Mysql Error %d: %s" % (e.args[0], e.args[1])
                return 1

        dlg = wx.MessageDialog(self,u'恭喜！该词库例句已经生成！！',
                                u'例句生成!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
        self.sentence_extract_statu.SetLabelText(u" ")




    def corpus_choice2_ChoiceOnChoice(self, event):
        event.Skip()
        select_choice = self.corpus_choice2_Choice.GetString(self.corpus_choice2_Choice.GetCurrentSelection())

        pages = gl.DB_CURSOR.execute("select en_word,score,cn_word,time_last from %s_word"%select_choice)
        print pages
        self.data_Grid.data =[ [i,j,k,v] for i,j,k,v in gl.DB_CURSOR.fetchall()]
        self.data_Grid.current_page = 1
        self.data_Grid.lib_name = select_choice
        self.data_Grid.update()
        self.down_Button.Enable()
        self.page_staticText.SetLabelText(u"[第%s页/共%s页]"%(self.data_Grid.current_page,pages//12+1))

    def up_ButtonOnButtonClick(self, event):
        event.Skip()
        self.data_Grid.pripage()
        current_page = self.data_Grid.current_page
        total_pages = len(self.data_Grid.data)//12+1
        self.page_staticText.SetLabelText(u"[第%s页/共%s页]"%(self.data_Grid.current_page,len(self.data_Grid.data)//12+1))
        if self.data_Grid.current_page <= 1:
            self.up_Button.Disable()
        if self.data_Grid.current_page<total_pages:
            self.down_Button.Enable()
    def down_ButtonOnButtonClick(self, event):
        event.Skip()
        self.data_Grid.nextpage()
        current_page = self.data_Grid.current_page
        total_pages = len(self.data_Grid.data)//12+1
        self.page_staticText.SetLabelText(u"[第%s页/共%s页]"%(current_page,total_pages))

        if self.data_Grid.current_page >= total_pages:
            self.down_Button.Disable()
        if self.data_Grid.current_page>1:
            self.up_Button.Enable()
    def export_radioBoxOnRadioBox(self, event):
        event.Skip()
        self.radio_select = event.GetInt()
        print self.radio_select
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
        content=[]
        if self.radio_select ==0:
            lib_name = self.corpus_choice2_Choice.GetString(self.corpus_choice2_Choice.GetCurrentSelection())
            n=gl.DB_CURSOR.execute("select en_word,score,cn_word,time_last from %s_word"%lib_name)
            content=gl.DB_CURSOR.fetchall()
            # for i,values in enumerate(content):
            #     print i,values
            print "select 0"
        else:

            contents = []
            gl.DB_CURSOR.execute("select lib_name from curpos")
            lib_names = [i[0]for i in gl.DB_CURSOR.fetchall()]

            for i in lib_names:
                gl.DB_CURSOR.execute("select en_word,score,cn_word,time_last from %s_word"%i)
                contents.append(gl.DB_CURSOR.fetchall())
            for values in contents:
                for i,j in enumerate(values):
                    content.append(j)
            # for id,value in enumerate(content):
            #     print id ,value
            print "select 1"
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
                fp.write(u"编号   |   特色词英文   | 特色评分  | 特色词中文  | 最后更改时间"+"\n\n")
                print content
                for ID,values in enumerate(content):
                    print values
                    fp.write(str(ID+1)+" :"+str(values[0])+"   "+str(values[1])+"   "+str(values[2])+"   "+str(values[3])+"\n\n")
                fp.close()
            except Exception,e:
                print e
            dlg.Destroy()
            self.message(info1=u"保存完成",info2=u"处理结果")
            dlg.Destroy()
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
                        <center><body>
                            <h1 style="text-align:center">特色词导出结果</h1>
                            <table border="1">
                            <tr>
                                <th>编号</th>
                                <th>特色词英语</th>
                                <th>特色评分</th>
                                <th>特色词中文</th>
                                <th>最后更改时间</th>
                            </tr>
                    '''
            for ID,values in enumerate(content):
                html_style += """
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                              """%(ID,str(values[0]),str(values[1]),str(values[2]),str(values[3]))
            html_style += """
                                    </table></center>
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
        for i ,label in enumerate([u"编号",u"特色词英文",u"特色评分",u"特色词中文",u"最后更改时间"]):
            xls_table.write(0,i,label,xls_style)
        for ID,value in enumerate(content):
            xls_table.write(ID+1,0,ID+1,xls_style)
            xls_table.write(ID+1,1,value[0],xls_style)
            xls_table.write(ID+1,2,value[1],xls_style)
            xls_table.write(ID+1,3,value[2],xls_style)
            xls_table.write(ID+1,4,value[3],xls_style)
        xls_file.save(path)

        dlg.Destroy()
        self.message(info1=u"保存完成",info2=u"处理结果")

    def message(self,info1=None,info2=None):
        dlg = wx.MessageDialog(self,u'%s！'%info1,
                                u'%s!'%info2,
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()










    def update_corpus_Choice(self):
        folder_list = os.listdir(gl.CWD+"\\Data\\cleaned\\")
        corpus_ChoiceChoices=[]
        for i in folder_list:
            if os.path.isdir(gl.CWD+"\\Data\\cleaned\\"+i):
                corpus_ChoiceChoices.append(i)
        self.corpus_Choice.Clear()

        self.corpus_Choice.AppendItems([i for i in corpus_ChoiceChoices])
        print "extract update"
        return corpus_ChoiceChoices

    def update_corpus_choice2_Choice(self):
        corpus_choice2_ChoiceChoices=[]
        gl.DB_CURSOR.execute("select lib_name from curpos")
        for i in gl.DB_CURSOR.fetchall():
            corpus_choice2_ChoiceChoices.append(i[0])
        return corpus_choice2_ChoiceChoices
