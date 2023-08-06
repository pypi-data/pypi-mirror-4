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
debug("Initializing stage...", 1)
from .stage import Stage
debug("Done.", -1)
debug("Initializing sprite panel...", 1)
from .spritePanel import SpritePanel
debug("Done.", -1)


class RightPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        debug("Making stage...", 1)
        self.stage = Stage(self)
        debug("Done.", -1)

        debug("Making sprite panel...", 1)
        self.spritePanel = SpritePanel(self)
        debug("Done.", -1)

        self.sizer.Add(self.stage, 0)
        self.sizer.Add(self.spritePanel, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.SetMinSize((480, self.GetSize()[1]))
