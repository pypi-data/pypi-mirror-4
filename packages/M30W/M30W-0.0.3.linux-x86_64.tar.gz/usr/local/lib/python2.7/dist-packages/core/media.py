"""Handles media and makes them available platform-independent.
"""
from os.path import join
import wx


class _Provider():
    def __init__(self, path):
        self.path = path

    def __call__(self, name, format=wx.Bitmap, ext='.png'):
        if format == wx.Bitmap:
            return wx.Bitmap(join(self.path, name + ext),
                              wx.BITMAP_TYPE_ANY)
        if format == wx.Image:
            return wx.Image(join(self.path, name + ext),
                              wx.BITMAP_TYPE_ANY)
        if format == wx.Icon:
            return wx.Icon(join(self.path, name + ext),
                              wx.BITMAP_TYPE_ANY)

get_icon = _Provider(join('core', 'icons'))
