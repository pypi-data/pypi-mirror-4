import wx
from M30W.debug import debug
from M30W import runtime
from M30W import media, config

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

        self.SetSize(config.get_option('START_SIZE', self.GetSize(), True))
        self.Maximize(config.get_option('START_MAXIMIZED', False, True))

        self.SetIcon(media.get_icon('M30W', wx.Icon, '.ico'))
        wx.GetApp().SetTopWindow(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

    def OnClose(self, event):
        debug("Saving frame size...", 1)
        config.set_option('START_SIZE', self.GetSize())
        config.set_option('START_MAXIMIZED', self.IsMaximized())

        debug("Done.", -1)
        self.Destroy()
