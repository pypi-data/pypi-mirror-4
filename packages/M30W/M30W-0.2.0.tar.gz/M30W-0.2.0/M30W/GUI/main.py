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
import traceback
from M30W.debug import debug, DEBUG
from M30W import config
from M30W import runtime
#Trying to import wx, raising an error message using Tkinter if not found.
try:
    debug("Importing wxPython...", 1)
    debug("Ensuring version 2.8...")
    #import wxversion
    #wxversion.ensureMinimal('2.8')
    debug("Importing wx...")
    import wx
    debug("Done.", -1)
except ImportError:
    from Tkinter import *
    import tkMessageBox
    root = Tk()
    root.withdraw()
    print "No wxPython found! Please install it from wxpython.org!"
    tkMessageBox.showerror("No wx found!",
                            "Please install it from wxpython.org!")
    sys.exit("No wxPython module was found on this computer!")

#Enable for debugging through Ctrl+Alt+I
#from wx.lib.mixins.inspection import InspectableApp
#class App(InspectableApp):
class App(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)
        self.SetAppName("M30W")
        self._org_except_hook = sys.excepthook
        def excepthook(type, obj, tb):
            dlg = wx.MessageDialog(None, "M30W encountered an error:\n%s"
                                         "\nDo You want to abort?"
                                         % '\n'.join(
                                traceback.format_exception(type, obj, tb)
                                                     ),
                                   "M30W encountered an error!",
                                   wx.ICON_ERROR | wx.CANCEL | wx.OK)
            if dlg.ShowModal() == wx.ID_OK:
                self.GetTopWindow().Close()
                self._org_except_hook(type, obj, tb)

        if not DEBUG: sys.excepthook = excepthook

    def CreateGUI(self):
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        debug("Making main frame...", 1)
        self.mainFrame = MainFrame(None)
        debug('Done.', -1)

        debug('Showing main frame...')
        self.mainFrame.Show(True)
        debug("Done.")

    def OnExit(self):
        config.save()


def init_app():
    global MainFrame
    debug("Initializing main frame...", 1)
    from .mainFrame import MainFrame
    debug('Done.', -1)


def show_app():
    #Creating app here to avoid wx._core.PyNoAppError
    app = App()

    debug("Initializing app...", 1)
    init_app()
    debug("Done.", -1)

    debug("Creating GUI...", 1)
    app.CreateGUI()
    debug("Done.", -1)

    debug("Starting main loop...")
    app.MainLoop()
