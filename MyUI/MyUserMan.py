# coding:utf-8

import wx
import wx.dataview as dv
import images
from Utils import gl, md5
import datetime
###########################################################################
## 用户管理
###########################################################################

class MyUserMan(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)

        self.set_power = None
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        Panel_bSizer = wx.BoxSizer(wx.VERTICAL)

        userinfo_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"当前存在的用户信息"), wx.VERTICAL)

        Panel_bSizer.Add(userinfo_sbSizer, 1, wx.EXPAND, 5)

        createuser_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"创建新用户"), wx.VERTICAL)

        gSizer1 = wx.GridSizer(0, 2, 0, 0)


        # create the listctrl
        self.dvlc = dv.DataViewListCtrl(self)
        # Give it some columns.
        # The ID col we'll customize a bit:
        self.dvlc.AppendTextColumn(u'用户名', width=170)
        self.dvlc.AppendTextColumn(u'用户权限', width=170)
        self.dvlc.AppendTextColumn(u'用户创建时间', width=260)
        self.dvlc.AppendTextColumn(u'用户最后操作时间', width=170)

        self.ShowUserInfo()
        # Set the layout so the listctrl fills the panel
        # self.Sizer = wx.BoxSizer()
        userinfo_sbSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.delete_Button = wx.Button(userinfo_sbSizer.GetStaticBox(), wx.ID_ANY, u"删除选定的用户", wx.DefaultPosition,
                                       wx.DefaultSize,
                                       0)

        userinfo_sbSizer.Add(self.delete_Button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.name_staticText = wx.StaticText(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"请输入用户名称",
                                             wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.name_staticText.Wrap(-1)
        gSizer1.Add(self.name_staticText, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.name_textCtrl = wx.TextCtrl(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"username",
                                         wx.DefaultPosition,
                                         wx.Size(200, -1), 0)
        gSizer1.Add(self.name_textCtrl, 0, wx.ALL, 5)

        self.pwd_staticText = wx.StaticText(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"请输入用户密码",
                                            wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.pwd_staticText.Wrap(-1)
        gSizer1.Add(self.pwd_staticText, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.pwd_textCtrl = wx.TextCtrl(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"userpwd", wx.DefaultPosition,
                                        wx.Size(200, -1), 0)
        gSizer1.Add(self.pwd_textCtrl, 0, wx.ALL, 5)

        self.power_staticText = wx.StaticText(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"请输入用户权限",
                                              wx.DefaultPosition,
                                              wx.DefaultSize, 0)
        self.power_staticText.Wrap(-1)
        gSizer1.Add(self.power_staticText, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        power_choiceChoices = [u"无创建用户权利的用户", u"有创建用户权利的用户"]
        self.power_choice = wx.Choice(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                      wx.Size(200, -1),
                                      power_choiceChoices, wx.CB_SORT)
        self.power_choice.SetSelection(0)
        gSizer1.Add(self.power_choice, 0, wx.ALL, 5)

        self.confirm_Button = wx.Button(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"创建用户", wx.Point(-1, -1),
                                        wx.DefaultSize, 0)
        gSizer1.Add(self.confirm_Button, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.cancel_Button = wx.Button(createuser_sbSizer.GetStaticBox(), wx.ID_ANY, u"取消创建", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        gSizer1.Add(self.cancel_Button, 0, wx.ALL, 5)

        createuser_sbSizer.Add(gSizer1, 1, wx.EXPAND, 5)

        Panel_bSizer.Add(createuser_sbSizer, 1, wx.EXPAND, 5)
        print gl.USER_POWER
        if gl.USER_POWER != u"管理员":
            self.delete_Button.Disable()
            self.confirm_Button.Disable()
            self.cancel_Button.Disable()
        self.SetSizer(Panel_bSizer)
        self.Layout()

        # Connect Events

        self.delete_Button.Bind(wx.EVT_BUTTON, self.delete_ButtonOnButtonClick)
        self.confirm_Button.Bind(wx.EVT_BUTTON, self.confirm_ButtonOnButtonClick)
        self.cancel_Button.Bind(wx.EVT_BUTTON, self.cancel_ButtonOnButtonClick)
        self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.power_choice)

    def __del__(self):
        pass


    # Virtual event handlers, overide them in your derived class

    def EvtChoice(self, event):
        event.Skip()
        self.set_power = event.GetString()

    def delete_ButtonOnButtonClick(self, event):
        event.Skip()
        row = self.dvlc.GetSelectedRow()
        if row == -1:
            dlg = wx.MessageDialog(self, u'请先点击选取一行，再进行删除!',
                                   u'操作错误',
                                   wx.OK | wx.ICON_ERROR
                                   # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return 0

        delet_name = self.dvlc.GetValue(row=row, col=0)
        if delet_name == gl.USER_NAME:
            dlg = wx.MessageDialog(self, u'管理员不能删除自己的账号!',
                                   u'操作错误',
                                   wx.OK | wx.ICON_ERROR
                                   # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return 0

        sql = "DELETE FROM user WHERE user_name = '%s' " % delet_name  # LIMIT 6;
        gl.DB_CURSOR.execute(sql)
        gl.DB_CONN.commit()
        self.ShowUserInfo()

    def confirm_ButtonOnButtonClick(self, event):
        event.Skip()
        temp_name = self.name_textCtrl.GetValue()
        temp_pwd = self.pwd_textCtrl.GetValue()
        user_name = md5.md5(temp_name)
        # print user_name
        user_pwd = md5.md5(temp_pwd)
        user_power = 0 if self.set_power == u"无创建用户权利的用户" else 1
        print user_power
        if len(temp_name) < 5 or len(temp_name) > 20 or len(temp_pwd) < 5 or len(temp_pwd) > 20:
            dlg = wx.MessageDialog(self, u'信息填写有误，请填写5-20位的用户名和密码!',
                                   u'信息填写有误',
                                   wx.OK | wx.ICON_ERROR
                                   # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        user_name = str(temp_name)
        # print user_name
        user_pwd = md5.md5(str(temp_pwd))
        user_power = 1 if self.set_power == u"有创建用户权利的用户" else 0
        print user_name
        print user_power
        try:


            timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print timenow
            sql = "insert into user(user_name,user_pwd,user_power,time_created,time_last) values('%s','%s',%s,'%s','%s');"  # now()
            param = (user_name, user_pwd, user_power, timenow, timenow)
            gl.DB_CURSOR.execute(sql % param)
            gl.DB_CONN.commit()
            print "success"
        except:
            print "erro"
        self.ShowUserInfo()


    def cancel_ButtonOnButtonClick(self, event):
        event.Skip()


    def ShowUserInfo(self):
        self.dvlc.DeleteAllItems()
        sql = "select user_name,user_power,time_created,time_last from user;"
        try:
            n = gl.DB_CURSOR.execute(sql)
        except:
            pass
        info = gl.DB_CURSOR.fetchall()
        if n >= 1:
            for i in info:
                print i
                i = list(i)
                i[1] = u"管理员" if i[1] == 1 else u"普通用户"
                i[2] = str(i[2])
                i[3] = str(i[3])

                self.dvlc.AppendItem(list(i))