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
