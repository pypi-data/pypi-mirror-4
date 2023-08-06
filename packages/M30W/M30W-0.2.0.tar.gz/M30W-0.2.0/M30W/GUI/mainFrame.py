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
from M30W.debug import debug
from M30W import runtime, media
from M30W.config import config 

debug("Initializing menus...", 1)
from .menu import menus, MenuBar, SaveBeforeClosing
debug("Done.", -1)
debug("Initializing right panel...", 1)
from .rightPanel import RightPanel
debug("Done.", -1)
debug("Initializing left panel...", 1)
from .leftPanel import LeftPanel
debug("Done.", -1)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        runtime.mainFrame = self
        self.SetTitle('M30W')

        debug("Making menus...", 1)
        menubar = MenuBar(self, menus)
        self.SetMenuBar(menubar)
        debug("Done.", -1)

        debug('Making right panel...', 1)
        self.right_pane = RightPanel(self)
        debug("Done.", -1)

        debug("Making left panel...", 1)
        self.left_pane = LeftPanel(self)
        debug("Done.", -1)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.left_pane, 1, flag=wx.EXPAND)
        self.sizer.Add(self.right_pane, 0, flag=wx.EXPAND | wx.LC_ICON)
        self.SetSizerAndFit(self.sizer)

        self.SetMinSize(self.GetSize())

        self.SetSize(config.get('START_SIZE'))
        self.Maximize(config.setdefault('START_MAXIMIZED', False))

        self.SetIcon(media.get_icon('M30W', wx.Icon, '.ico'))
        wx.GetApp().SetTopWindow(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

    def OnClose(self, event):
        if SaveBeforeClosing(event) == wx.ID_CANCEL:
            return event.Veto()
        debug("Saving frame size...", 1)
        config['START_SIZE'] = tuple(self.GetSize())
        config['START_MAXIMIZED'] = self.IsMaximized()

        debug("Done.", -1)
        self.Destroy()
