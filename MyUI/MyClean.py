# -*- coding: utf-8 -*-

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import sys,os
from Core.specificwords_extract import *
from Utils import gl

###########################################################################
## 数据清洗（Read - Clean - load）
###########################################################################





class MyClean(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)

        self.input_path = None
        # self.cleaned_path=None
        self.input_type = None
        self.file_folder = None
        self.clean_out_folder = None
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"第一步：打开语料库文件夹"), wx.HORIZONTAL)
        self.m_button2 = wx.Button(sbSizer1.GetStaticBox(), wx.ID_ANY, u"打开", wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer1.Add(self.m_button2, 0, wx.ALL, 5)
        bSizer1.Add(sbSizer1, 1, wx.EXPAND, 5)

        sbSizer2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"第二步：清洗并导入数据"), wx.HORIZONTAL)
        self.m_button3 = wx.Button(sbSizer2.GetStaticBox(), wx.ID_ANY, u"开始", wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer2.Add(self.m_button3, 0, wx.ALL, 5)
        bSizer1.Add(sbSizer2, 1, wx.EXPAND, 5)


        sbSizer1_1 = wx.StaticBoxSizer(wx.StaticBox(sbSizer1.GetStaticBox(), wx.ID_ANY, u"语料库文件夹中的文件"), wx.HORIZONTAL)
        self.list1 = CheckListCtrl(sbSizer1_1.GetStaticBox())
        sbSizer1_1.Add(self.list1, 1, wx.EXPAND,0)



        sbSizer2_1 = wx.StaticBoxSizer(wx.StaticBox(sbSizer2.GetStaticBox(), wx.ID_ANY, u"清洗后的文件"), wx.HORIZONTAL)
        self.list2 = CheckListCtrl(sbSizer2_1.GetStaticBox())
        sbSizer2_1.Add(self.list2, 1, wx.EXPAND,1)





        sbSizer1.Add(sbSizer1_1, 1, wx.EXPAND,0)
        sbSizer2.Add(sbSizer2_1, 1, wx.EXPAND,0)



        self.SetCheckList(self.list1)
        self.SetCheckList(self.list2)


        self.SetSizer(bSizer1)
        self.Layout()
        # Connect Events
        self.m_button2.Bind(wx.EVT_BUTTON, self.m_button2OnButtonClick)
        self.m_button3.Bind(wx.EVT_BUTTON, self.m_button3OnButtonClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list1)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list1)
        # self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list2)
        # self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list2)

    def __del__(self):
        pass


    # Virtual event handlers, overide them in your derived class
    def m_button2OnButtonClick(self, event):
        event.Skip()
        dlg = wx.DirDialog(self, u"选取一个文件夹:",
                           style=wx.DD_DEFAULT_STYLE
                           # | wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
        )

        # If the user selects OK, then process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it.
        if dlg.ShowModal() == wx.ID_OK:
            self.input_path = dlg.GetPath()
            self.file_folder = self.input_path.split("\\")[-1]
            print (u'你选取了: %s\n' % self.input_path)
            corpus_files = os.listdir(self.input_path)
            try:
                temp_type = corpus_files[0].split(".")[-1].lower()
                if temp_type == "txt":
                    self.input_type = "txt"
                elif temp_type == "html" or temp_type == "htm":
                    self.input_type = "html"
                else:
                     dlg = wx.MessageDialog(self, u'格式错误!',
                               u'不支持所打开文件夹内语料库格式！',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
                     dlg.ShowModal()
                     dlg.Destroy()
                     return 1
            except:
                self.input_type="html"


            self.list1.ClearAll()
            self.SetCheckList(self.list1)

            for ID, data in enumerate(corpus_files):
                index = self.list1.InsertStringItem(sys.maxint,str(ID+1))
                self.list1.SetStringItem(index, 1, data)
                self.list1.SetStringItem(index, 2, data.decode("utf-8").encode("gbk").split(".")[-1])
                self.list1.SetStringItem(index, 3, self.input_path+"\\"+data)
                self.list1.SetItemData(index, index + 1)
                self.list1.CheckItem(ID)




        # Only destroy a dialog after you're done with it.
        dlg.Destroy()

    def m_button3OnButtonClick(self, event):
        event.Skip()

        if self.input_path == None:
            dlg = wx.MessageDialog(self,u'尚未导入语料库，请先导入语料库文件夹再进行本操作！',
                                u'未导入语料库!',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return 1
        dlg = wx.MessageDialog(self,u'如要开始，将会把先前已经清洗的数据删除！！',
                                u'警告!',
                               wx.YES_NO | wx.YES_DEFAULT |  wx.ICON_WARNING
                               )
        if dlg.ShowModal() == wx.ID_NO:
            return 0

        dlg.Destroy()
        self.m_button3.SetLabelText(u"正在清洗")
        origin_color=self.m_button3.GetBackgroundColour()
        self.m_button3.SetBackgroundColour(wx.RED)
        self.m_button3.Disable()
        self.clean_out_folder = gl.CWD+"\\Data\\cleaned\\%s"%self.file_folder
        if os.path.exists(self.clean_out_folder):
            # os.removedirs("Data\\cleaned")
            try:
                __import__('shutil').rmtree(self.clean_out_folder)
                os.mkdir(self.clean_out_folder)
            except Exception , e:
                print e
        else:
            os.mkdir(self.clean_out_folder)

        if self.input_type =="html":

            clean_html(self.input_path+u"\\",self.clean_out_folder+"\\")
        elif self.input_type == "txt":
            clean_taggedtxt(self.input_path+u"\\",self.clean_out_folder+"\\")
        # print "test1"
        self.list2.ClearAll()
        self.SetCheckList(self.list2)
        # print "test2"
        for ID, data in enumerate(os.listdir(gl.CWD+"\\Data\\cleaned\\%s"%self.file_folder)):
            print ID,data
            # print "test3"
            index = self.list2.InsertStringItem(sys.maxint,str(ID+1))
            # print "test4"
            self.list2.SetStringItem(index, 1, data)
            # print "test5"
            self.list2.SetStringItem(index, 2, data.split(".")[-1])
            # print "test6"
            self.list2.SetStringItem(index, 3, gl.CWD+self.clean_out_folder+"\\"+data)
            # print "test7"
            self.list2.SetItemData(index, index + 1)
            # print "test8"
            # self.list2.CheckItem(ID)
        self.m_button3.SetLabelText(u"开始")
        self.m_button3.SetBackgroundColour(origin_color)
        self.m_button3.Enable()
        dlg = wx.MessageDialog(self,u'恭喜！数据已经清洗完成！！',
                                u'清洗完成!',
                               wx.OK | wx.ICON_INFORMATION#wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()


    def SetCheckList(self,List):
        List.InsertColumn(0, u"ID",wx.LIST_FORMAT_CENTER)
        List.InsertColumn(1, u"文件名",wx.LIST_FORMAT_CENTER)
        List.InsertColumn(2, u"文件格式", wx.LIST_FORMAT_CENTER)
        List.InsertColumn(3, u"文件地址",wx.LIST_FORMAT_CENTER)

        # for key, data in musicdata.iteritems():
        #     index = self.list1.InsertStringItem(sys.maxint, data[0])
        #     self.list1.SetStringItem(index,0,str(index+1))
        #     self.list1.SetStringItem(index,1,data[0])
        #     self.list1.SetStringItem(index, 2, data[1])
        #     self.list1.SetStringItem(index, 3, data[2])
        #     self.list1.SetItemData(index, index+1)

        List.SetColumnWidth(0, 50)
        List.SetColumnWidth(1, 100)
        List.SetColumnWidth(2, 100)
        List.SetColumnWidth(3, 240)



    def OnItemSelected(self, evt):
        print ('item selected: %s\n' % evt.m_itemIndex)

    def OnItemDeselected(self, evt):
        print ('item deselected: %s\n' % evt.m_itemIndex)

    # def test(self):
    #     print "success"


