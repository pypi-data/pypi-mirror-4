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

import wx
from wx.lib.filebrowsebutton import FileBrowseButton as BrowseButton
from M30W.config import config

class Item(wx.Panel):
    def __init__(self, parent, infos):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.token = infos['token']
        self.type = infos['type']

        {'path': self.MakePath}[infos['type']](infos)

        self.SetSizerAndFit(self.sizer)

    def __repr__(self):
        return "<Item token=%s type=%s at %s>" % (self.token,
                                                  self.type,
                                                  id(self))

    def MakePath(self, infos):
        self.button = BrowseButton(self,
                                   labelText=infos['label'],
                                   fileMask=infos['pattern'])
        self.button.SetValue(config.get(self.token, ""))
        self.button.textControl.SetEditable(False)
        self.sizer.Add(self.button, 1, flag=wx.EXPAND)
        def get():
            return self.button.GetValue()
        self.GetValue = get

    def GetValue(self):
        raise NotImplementedError

class PreferencesDialog(wx.Dialog):
    settings = \
    ({'token': "SCRATCH_PATH",
      'label': "Scratch' Location:",
      'type': "path",
      'pattern': "*.*"},
     {'token': "IMAGE_EDITOR_PATH",
      'label': "Image Editor's Path:",
      "type": "path",
      'pattern': "*.*"})

    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self.items = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for item in self.settings:
            self.items.append(Item(self, item))
            self.sizer.Add(self.items[-1])

        self.buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.buttonsSizer)

        self.cancel = wx.Button(self, wx.ID_CANCEL)
        self.apply = wx.Button(self, wx.ID_APPLY)

        self.buttonsSizer.AddStretchSpacer(2)
        self.buttonsSizer.Add(self.cancel, 1)
        self.buttonsSizer.Add(self.apply, 1)

        self.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy(), self.cancel)
        self.Bind(wx.EVT_BUTTON, self.OnApply, self.apply)

        self.SetSizerAndFit(self.sizer)
        self.Layout()
        self.Show()

    def OnApply(self, evt):
        for item in self.items:
            config[item.token] = item.GetValue()
        self.Destroy()

