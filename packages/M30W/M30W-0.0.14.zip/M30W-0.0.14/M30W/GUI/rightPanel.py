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
