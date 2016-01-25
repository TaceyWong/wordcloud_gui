#coding:utf-8
import wx
import wx.lib.colourselect as csel

try:
    from agw import pyprogress as PP
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.pyprogress as PP


class PyProgressDemo(wx.Panel):

    def __init__(self, parent,colour,label):

        wx.Panel.__init__(self, parent)

        self.panel = wx.Panel(self, -1)        

        
        self.LayoutItems()


    def LayoutItems(self):

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        rightsizer = wx.FlexGridSizer(7, 2, 5, 5)

        startbutton = wx.Button(self.panel, -1, "Start PyProgress!")

        self.elapsedchoice = wx.CheckBox(self.panel, -1, "Show Elapsed Time")
        self.elapsedchoice.SetValue(1)

        self.cancelchoice = wx.CheckBox(self.panel, -1, "Enable Cancel Button")
        self.cancelchoice.SetValue(1)

        static1 = wx.StaticText(self.panel, -1, "Gauge Proportion (%): ")
        self.slider1 = wx.Slider(self.panel, -1, 20, 1, 99, style=wx.SL_HORIZONTAL|
                                 wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.slider1.SetTickFreq(10, 1)
        self.slider1.SetValue(20)

        static2 = wx.StaticText(self.panel, -1, "Gauge Steps: ")
        self.slider2 = wx.Slider(self.panel, -1, 50, 2, 100, style=wx.SL_HORIZONTAL|
                                 wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.slider2.SetTickFreq(10, 1)
        self.slider2.SetValue(50)

        static3 = wx.StaticText(self.panel, -1, "Gauge Background Colour: ")
        self.csel3 = csel.ColourSelect(self.panel, -1, "Choose...", wx.WHITE)

        static4 = wx.StaticText(self.panel, -1, "Gauge First Gradient Colour: ")
        self.csel4 = csel.ColourSelect(self.panel, -1, "Choose...", wx.WHITE)

        static5 = wx.StaticText(self.panel, -1, "Gauge Second Gradient Colour: ")
        self.csel5 = csel.ColourSelect(self.panel, -1, "Choose...", wx.BLUE)

        rightsizer.Add(self.elapsedchoice, 0, wx.EXPAND|wx.TOP, 10)
        rightsizer.Add((10, 0))
        rightsizer.Add(self.cancelchoice, 0, wx.EXPAND|wx.TOP, 3)
        rightsizer.Add((10, 0))
        rightsizer.Add(static1, 0, wx.ALIGN_CENTER_VERTICAL, 10)
        rightsizer.Add(self.slider1, 0, wx.EXPAND|wx.TOP, 10)
        rightsizer.Add(static2, 0, wx.ALIGN_CENTER_VERTICAL, 10)
        rightsizer.Add(self.slider2, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)
        rightsizer.Add(static3, 0, wx.ALIGN_CENTER_VERTICAL)
        rightsizer.Add(self.csel3, 0)
        rightsizer.Add(static4, 0, wx.ALIGN_CENTER_VERTICAL)
        rightsizer.Add(self.csel4, 0)
        rightsizer.Add(static5, 0, wx.ALIGN_CENTER_VERTICAL)
        rightsizer.Add(self.csel5, 0)
        
        mainsizer.Add(startbutton, 0, wx.ALL, 20)
        mainsizer.Add(rightsizer, 1, wx.EXPAND|wx.ALL, 10)

        self.panel.SetSizer(mainsizer)
        mainsizer.Layout()

        framesizer = wx.BoxSizer(wx.VERTICAL)
        framesizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(framesizer)
        framesizer.Layout()

        startbutton.Bind(wx.EVT_BUTTON, self.OnStartProgress)
        
        
    def OnStartProgress(self, event):

        event.Skip()
                
        style = wx.PD_APP_MODAL
        if self.elapsedchoice.GetValue():
            style |= wx.PD_ELAPSED_TIME
        if self.cancelchoice.GetValue():
            style |= wx.PD_CAN_ABORT

        dlg = PP.PyProgress(None, -1, u"数据处理",
                            u"数据处理中……",
                            agwStyle=style)

        proportion = self.slider1.GetValue()
        steps = self.slider2.GetValue()
        
        backcol = self.csel3.GetColour()
        firstcol = self.csel4.GetColour()
        secondcol = self.csel5.GetColour()

        dlg.SetGaugeProportion(20/100.0)
        dlg.SetGaugeSteps(50)
        dlg.SetGaugeBackground(wx.RED)
        dlg.SetFirstGradientColour(wx.WHITE)
        dlg.SetSecondGradientColour(wx.BLUE)
        
        max = 400
        keepGoing = True
        count = 0

        while keepGoing and count < max:
            count += 1
            wx.MilliSleep(30)

            if count >= max / 2:
                keepGoing = dlg.UpdatePulse("Half-time!")
            else:
                keepGoing = dlg.UpdatePulse()

        dlg.Destroy()
        wx.SafeYield()
        wx.GetApp().GetTopWindow().Raise()



if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(parent=None)
    pan = PyProgressDemo(parent=frame)
    frame.Show()
    app.MainLoop()
