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

from __future__ import division
from math import radians, degrees, hypot, atan2, sin, cos, pi
import wx, time
from M30W import runtime
from M30W.costume import _convert
from M30W.debug import debug
from M30W.sprites import NORMAL, RL


#Need to switch to canvas?
class Stage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        runtime.stage = self
        self.SetSizeHints(480, 360, 480, 360)
        self.SetBackgroundColour(wx.WHITE)
        self.SetSize((480, 360))
        self.Bind(wx.EVT_PAINT, self.OnPaint, self)

    def OnPaint(self, event):
        debug("Redrawing stage...", 1)
        start = time.time()
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        stage = runtime.project.stage
        dc.DrawBitmap(stage.active_costume.get_image(), 0, 0)
        for sprite in runtime.get_sprites():
            if not sprite.visible: continue
            costume = sprite.active_costume
            image = costume.get_image(wx.Image)
            if sprite.rotmode == NORMAL:
                rotation = radians(360 - (sprite.direction - 90) % 360)
                image = image.Rotate(rotation, costume.center, True)
                center = [i // 2 for i in costume.size]
                c = hypot(center[0] - costume.center[0], 
                          center[1] - costume.center[1])
                rotation += atan2(center[1] - costume.center[1],
                                  center[0] - costume.center[0])
                center = [i // 2 for i in image.GetSize()]
                x, y = center[0] + cos(rotation) * -c, center[1] + sin(rotation) * -c
    
                x = sprite.truex - x
                y = sprite.truey - y
            elif sprite.rotmode == RL:
                if sprite.direction > 180:
                    image = image.Mirror()
                x = sprite.truex - costume.center[0]
                y = sprite.truey - costume.center[1]
            else:
                x = sprite.truex - costume.center[0]
                y = sprite.truey - costume.center[1]
            dc.DrawBitmap(_convert(image, wx.Bitmap), x, y)
        dc.EndDrawing()
        debug("Done. Took %3fs" % (time.time() - start), -1)

    def GetBitmap(self):
        context = wx.ClientDC(self)
        memory = wx.MemoryDC()
        x, y = self.ClientSize
        bitmap = wx.EmptyBitmap(x, y, -1)
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, x, y, context, 0, 0)
        memory.SelectObject(wx.NullBitmap)
        return bitmap
