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

"""Handles media and makes them available platform-independent.
"""
import os.path
import wx

M30W_FOLDER = os.path.split(__file__)[0]

class _Provider():
    def __init__(self, path):
        self.path = path

    def __call__(self, name, format=wx.Bitmap, ext='.png'):
        if format == wx.Bitmap:
            return wx.Bitmap(os.path.join(self.path, name + ext),
                              wx.BITMAP_TYPE_ANY)
        if format == wx.Image:
            return wx.Image(os.path.join(self.path, name + ext),
                              wx.BITMAP_TYPE_ANY)
        if format == wx.Icon:
            return wx.Icon(os.path.join(self.path, name + ext),
                              wx.BITMAP_TYPE_ANY)

get_icon = _Provider(os.path.join(M30W_FOLDER, 'icons'))
