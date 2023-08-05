import sys
import wx
from core.IO import save, save_as, open
from core.debug import debug, not_implemented, print_not_implemented_functions
from errorConsole import ErrorConsole
from core import media
import core.sprites


SEPARATOR = 'separator'
SUBMENU = 'submenu'


class Menu(wx.Menu):
    def __init__(self, parent, items, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.parent = parent
        for item, itemid, callback in items:
            if itemid == SEPARATOR:
                self.AppendSeparator()
            elif itemid == SUBMENU:
                self.AppendSubMenu()
            else:
                item = self.Append(itemid, item)
                self.parent.Bind(wx.EVT_MENU, callback, item)


class MenuBar(wx.MenuBar):
    def __init__(self, parent, menus, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        self.parent = parent
        global menubar
        menubar = self
        for title, items in menus:
            self.Append(Menu(self.parent, items), title)


@not_implemented
def OnNew(e):
    pass


def OnOpen(e):
    dialog = wx.FileDialog(None,
                           message="Please choose file",
                           wildcard="Scratch 1.4 project file (*.sb)|*.sb"
                                    "|All files (*.*)|*.*",
                           style=wx.OPEN)

    if dialog.ShowModal() == wx.ID_OK:
        open(dialog.GetPath())
    dialog.Destroy()


def OnSave(e):
    try:
        save()
    except ValueError:
        OnSaveAs(e)

def OnSaveAs(e):
    dialog = wx.FileDialog(None,
                           message="Please choose file",
                           wildcard="Scratch 1.4 project file (*.sb)|*.sb"
                                    "|All files (*.*)|*.*",
                           style=wx.SAVE)

    if dialog.ShowModal() == wx.ID_OK:
        save_as(dialog.GetPath())
    dialog.Destroy()


def OnQuit(e):
    wx.GetApp().GetTopWindow().Close()


def OnAbout(e):
    description = """M30W is a program designed to allow fast
developing of Scratch projects.
It uses a unique text syntax to allow typing of
blocks rather than laggy dragging them around."""
    mlicense = """M30W is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/"""
    info = wx.AboutDialogInfo()

    info.SetIcon(media.get_icon('M30W', wx.Icon, '.ico'))
    info.SetName('M30W')
    info.SetVersion('prototype')
    info.SetDescription(description)
    info.SetCopyright('(C) 2012 M30W developers')
    info.SetWebSite('http://scratch.mit.edu/forums/viewtopic.php?id=106225')
    info.SetLicence(mlicense)

    wx.AboutBox(info)


def OnConsole(event):
    sys.stdout = ErrorConsole(None)


def OnPrint(event):
    print_not_implemented_functions()


File = (('&New\tCtrl+N', wx.ID_NEW, OnNew),
        ('&Open\tCtrl+O', wx.ID_OPEN, OnOpen),
        (None, SEPARATOR, None),
        ('&Save\tCtrl+S', wx.ID_SAVE, OnSave),
        ('Save &As\tCtrl+Shift+S', wx.ID_SAVEAS, OnSaveAs),
        (None, SEPARATOR, None),
        ('&Quit', wx.ID_EXIT, OnQuit))
Edit = ()
Help = [('Error Console', wx.ID_ANY, OnConsole),
        ('Print not implemented functions', wx.ID_ANY, OnPrint),
        (None, SEPARATOR, None),
        ('About M30W', wx.ID_ABOUT, OnAbout)]
menus = (('&File', File), ('&Edit', Edit), ('&Help', Help))
