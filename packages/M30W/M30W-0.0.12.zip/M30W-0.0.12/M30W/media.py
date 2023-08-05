"""Handles media and makes them available platform-independent.
"""
import os.path
import wx
import base64

M30W_FOLDER = os.path.split(__file__)[0]

image = """\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAADP0Myv4uLg6+Li4Ovh4uDr4eLe6+Dh3uvg4d7r4OHd6+Dg3evg4N3r4ODd
697g3eve4Nzr3uDc693e3OvPz8yw4eLhy6Skof96fHf/enx3/3p8d/96fHf/enx4/3x+ev98fnr/
fH56/3p8d/95e3b/eXt2/3l7dv+dnpr/4uLg0OHi4MuhoJj/ZmBQ/2hiUv9tZ1j/aWRX/25oW/93
cWP/d3Fj/3VwYf9ybF7/bmhZ/2hiU/9mYFD/mZiP/+Di39Dh4eDLqKSW/4Z1Vf+Le13/kIFk/5SF
av+Ed2L/hntl/5iJb/+KfWT/kYFl/4x8Xv9/cFH/f21N/6Kcjf/g4N7Q4OHgy7Srmf+kiFz/qY9l
/66Vbf+zm3b/s516/62Xd/9zZU//n4RZ/5R5Tf9wWjj/gmhA/5l7Sv+roIv/3+De0OHi4Mu+spv/
vphf/8KeaP/FpHL/xKJu/66MV/+TcTz/fmAy/7SJR/+0iUf/a1Iq/7GHRv+0iUf/tKWK/9/f3tLf
4N/MxbWa/9SjW//Tolj/0p1K/9OeRP/OmUP/uYc8/2tOI//OlkP/o3c1/7+LPv/OlkP/zpZD/8Ox
k//i4uLV3Nzazsq2lP/opkT/665C//LGV//43X3/88tf/+uwQ/+ody7/bE0e/9WWO//opED/6KRA
/+qtU//ZyK3/5eXk2dXW1NTPtY3//LA+//zFSv/+9a3///i+//71s//9zFP//LI//1I5FP/8rz7/
/K8+//y3Uf/4xn3/z8e3/q+vq+HP0M7asp99/5ZzOv+ef0P/xK9v/8a1df/FsXL/ooZH/5Z0O/9F
NRv/lnM6/6CBTf+0nnn/urm0/7a3s/2GiYZS0tTR1rWtmP+Whmv/lYZq/5WGav+Vhmr/lIZp/5SF
af+UhWn/lIVp/56QeP+3rJr/vbiv/rGxrv19gHuTAAAAA6aopITT09HY09PR2NPT0djS09HY0tPR
2NLT0djS09HY0tPR2NPT0drV19Xdz9DO46KjntVkZGBFAAAABQAAAAAAAAABAAAABAAAAAQAAAAE
AAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
"""


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
