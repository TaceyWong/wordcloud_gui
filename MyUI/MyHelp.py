#coding:utf-8

import wx

__author__ = 'Tacey Wong'
__date__   = "2016年元月"

###########################################################################
##帮助
###########################################################################

class MyHelp(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_richText1 = wx.richtext.RichTextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                                    wx.TE_READONLY| wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.WANTS_CHARS)
        bSizer1.Add(self.m_richText1, 1, wx.EXPAND | wx.ALL, 5)

        self.m_hyperlink1 = wx.HyperlinkCtrl(self, wx.ID_ANY, u"Tacey 词云在线帮助文档", u"http://www.github.com/iTacey/wordcloud_gui/doc/online/help",
                                             wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE)
        bSizer1.Add(self.m_hyperlink1, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

    def __del__(self):
        pass

    def update_Choice(self):
        pass
        Help_Text=u"""
#Tacey 词云使用帮助

#一、通用设置的使用

+【边距】设置生成的词云图片的边距
+【宽度】设置词云图片的宽度
+【高度】设置词云图片的高度
+【选择字体】选择词云使用的字体（若想使用其他字体，只需将TTF字体文件放到软件安装目录的font目录下）
+【最大字体】设置词云中最大字体号
+【最小字体】设置慈云钟最小字体号
+【选择背景颜色】设置词云的背景颜色

#二、格式文件词云生成的使用

+   该页面用来生成格式文本的词云，格式文本的形式是{词:词频}（不带大括号），如：
+   -------------------------------------------------------
+   中:100
+   华:80
+   人:60
+   民:50
+   共:35
+   和:25
+   国:77
+   -------------------------------------------------------
+   【！注意！】文本必须使用UTF-8编码，冒号为英文冒号，每一个{词：词频}占据一行

#三、文本文件词云生成的使用

+   该页面用来生成文本文件的词云，需要同时选定停词表和目标文本文件
+   【！注意！】文本必须使用UTF-8编码

#四、Web文件词云的生成

+   该页面用来生成Web HTML文件的词云，需要选定停词表和目标HTML文件
+   【！注意！】文本必须使用UTF-8编码


#-------更多帮助内容，请点击左下角链接，浏览在线帮助文档---------
"""
        Help_Text = Help_Text.split("\n")
        self.m_richText1.Clear()
        for i in Help_Text:
            if i.startswith("#"):
                self.m_richText1.BeginAlignment(wx.TEXT_ALIGNMENT_CENTRE)
                self.m_richText1.WriteText(i[1:])
                self.m_richText1.Newline()
                self.m_richText1.EndAlignment()

            if i.startswith("+"):
                self.m_richText1.WriteText(i[1:])
                self.m_richText1.Newline()


