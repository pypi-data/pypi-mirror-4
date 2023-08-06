#This file is part of the M30W software.
#Copyright (C) 2013 M30W developers.
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

def inform(caption="", msg=""):
    dialog = wx.MessageDialog(None, message=msg, caption=caption,
                              style=wx.OK)
    dialog.ShowModal()
    dialog.Destroy()

def warn(caption="", msg=""):
    dialog = wx.MessageDialog(None, message=msg, caption=caption,
                              style=wx.OK | wx.ICON_EXCLAMATION)
    dialog.ShowModal()
    dialog.Destroy()

def error(caption="", msg=""):
    dialog = wx.MessageDialog(None, message=msg, caption=caption,
                              style=wx.OK | wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Destroy()

def ask(caption="", msg=""):
    dialog = wx.MessageDialog(None, message=msg, caption=caption,
                              style=wx.ICON_QUESTION | wx.YES_NO)
    value = dialog.ShowModal()
    dialog.Destroy()
    return value == wx.ID_YES

def open(msg="", wildcard="All files (*.*)|*.*"):
    dialog = wx.FileDialog(None, message=msg, wildcard=wildcard,
                           style=wx.OPEN)
    value = None
    if dialog.ShowModal() == wx.ID_OK:
        value = dialog.GetPath()
    dialog.Destroy()
    return value

def save(msg="", wildcard="All diles (*.*)|*.*"):
    dialog = wx.FileDialog(None, message=msg, wildcard=wildcard,
                           style=wx.SAVE)
    value = None
    if dialog.ShowModal() == wx.ID_OK:
        value = dialog.GetPath()
    dialog.Destroy()
    return value
