#This file is part of the M30W software.
#Copyright (C) 2012-2013 M30W developers.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

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
