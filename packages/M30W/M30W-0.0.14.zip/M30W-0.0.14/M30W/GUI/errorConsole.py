import sys
import wx


class ErrorConsole(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetMinSize((500, 400))
        self.SetTitle("Error Console")
        self.panel = wx.Panel(self)
        self.panel.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.textfield = wx.TextCtrl(self.panel,
                                     style=wx.TE_MULTILINE | wx.HSCROLL)
        self.textfield.Disable()
        self.panel.sizer.Add(self.textfield, 1, wx.EXPAND)
        self.panel.SetSizerAndFit(self.panel.sizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.Show(True)

    def OnClose(self, event):
        sys.stdout = sys.__stdout__
        event.Skip()

    def write(self, string):
        self.textfield.write(string)
