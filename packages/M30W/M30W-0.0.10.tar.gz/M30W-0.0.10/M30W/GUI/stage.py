import wx
from M30W import runtime


#Need to switch to canvas.
class Stage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        runtime.stage = self
        self.SetSizeHints(480, 360, 480, 360)
        self.SetBackgroundColour(wx.WHITE)
        self.SetSize((480, 360))
        self.Bind(wx.EVT_PAINT, self.OnPaint, self)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        stage = runtime.project.stage
        dc.DrawBitmap(stage.costumes[stage.costume].get_image(), 0, 0)
        dc.EndDrawing()

    def GetBitmap(self):
        context = wx.ClientDC( self )
        memory = wx.MemoryDC( )
        x, y = self.ClientSize
        bitmap = wx.EmptyBitmap( x, y, -1 )
        memory.SelectObject( bitmap )
        memory.Blit( 0, 0, x, y, context, 0, 0)
        memory.SelectObject( wx.NullBitmap)
        return bitmap