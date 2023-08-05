from __future__ import division

import weakref
import time
import wx
from wx import aui
from M30W.debug import debug, not_implemented
from M30W import runtime
import M30W.media as media
from M30W import costume


IMAGE  = 'imageeditor'
SOUND  = 'soundeditor'
SCRIPT = 'scripteditor'


welcome_text = \
"""
Welcome to M30W!

M30W is a program designed to allow fast developing of Scratch projects.
It uses a unique text syntax to allow typing of blocks rather than laggy
dragging them around.

M30W currently is in development process, and we haven't implemented
running scripts yet; Don't look for the green flag ;)
Editing scripts is working, but because we use kurt to parse scripts, 
current limitations apply:

- Take care with the "length of" block: strings aren't dropdowns, lists are

- length of [Hello!]      // string
- length of [list v]      // list

- Variable names (and possibly other values, such as broadcasts) can't:
  * contain special identifiers (like end, if, etc.)
  * have trailing whitespace
  * contain special characters, rather obviously: like any of []()<> or equals =
  * be named after a block, eg. a variable called "wait until"
"""


class ScriptEditor(wx.Panel):
    font = wx.Font(10, wx.FONTFAMILY_MODERN,
                             wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL)
    style = wx.TextAttr(font=font)
    style.SetTabs([25])
    #TODO: let the user config tab width (25 * chrs)

    def __init__(self, sprite, token, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.sprite = weakref.proxy(sprite, self.DeleteMyself)
        self.token = token
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.textCtrl = wx.TextCtrl(self,
                                    style=wx.TE_MULTILINE | wx.HSCROLL)
        self.textCtrl.SetFont(self.font)
        self.textCtrl.SetDefaultStyle(self.style)
        self.textCtrl.write(self.sprite.code)

        self.sizer.Add(self.textCtrl, 1, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)
        self.Bind(wx.EVT_TEXT, self.Save, self.textCtrl)
        self.lastsave = time.time()

    def Save(self, event):
        ##Allows undo&redo
        #if time.time() - self.lastletter > 0.3:
            #self.undo.append(self.textCtrl.GetValue())
        self.lastsave = time.time()
        self.sprite.code = self.textCtrl.GetValue()

    @not_implemented
    def OnRedo(self):
        pass

    @not_implemented
    def OnUndo(self):
        pass

    def DeleteMyself(self, proxy):
        leftPanel = self.GetParent().GetParent()
        wx.CallAfter(leftPanel.RemovePageByToken, self.token)


class ImageEditor(wx.Listbook):
    def __init__(self, sprite, *args, **kwargs):
        wx.Listbook.__init__(self, *args, style=wx.LB_BOTTOM)

        self.sprite = sprite
        self.il = wx.ImageList(32, 32)
        self.names = []
        self.AssignImageList(self.il)

        #object because we imported costume
        for object in self.sprite.costumes:
            self.il.Add(object.get_thumbnail(32, costume.FORMAT_BITMAP))
            self.AddPage(ResourceViewer(self,
                                        object,
                                        True),
                         object.name,
                         select=True,
                         imageId=self.il.GetImageCount() - 1
                         )

    def UpdateList(self):
        pass


class ResourceViewer(wx.Panel):
    def __init__(self, parent, resource, costume=True):
        wx.Panel.__init__(self, parent, style=wx.FULL_REPAINT_ON_RESIZE)
        self.resource = resource
        self.costume = costume

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_BOTTOM)
        self.Bind(wx.EVT_MENU,
                  self.OnCenter,
                  self.toolbar.AddSimpleTool(wx.ID_ANY,
                                             media.get_icon('center'),
                                             shortHelpString="Center"))
        self.Bind(wx.EVT_MENU,
                  self.OnDuplicate,
                  self.toolbar.AddSimpleTool(wx.ID_ANY,
                                             media.get_icon('duplicate'),
                                             shortHelpString="Duplicate"))
        self.toolbar.Realize()

        if self.costume:
            self.sizer.AddSpacer(10, 10)
            self.xText = wx.StaticText(self, wx.ID_ANY, label="X:")
            self.sizer.Add(self.xText, 0, border=5,
                           flag=wx.ALIGN_BOTTOM | wx.BOTTOM)

            self.xCtrl = wx.SpinCtrl(self,
                                 wx.ID_ANY,
                                 initial=self.resource.get_center()[0],
                                 min=0,
                                 max=self.resource.get_size()[0] - 1)
            self.sizer.Add(self.xCtrl, 0, flag=wx.ALIGN_BOTTOM)

            self.sizer.AddSpacer(5, 5)

            self.yText = wx.StaticText(self, wx.ID_ANY, label="Y:")
            self.sizer.Add(self.yText, 0, border=5,
                           flag=wx.ALIGN_BOTTOM | wx.BOTTOM)

            self.yCtrl = wx.SpinCtrl(self,
                                 wx.ID_ANY,
                                 initial=self.resource.get_center()[1],
                                 min=0,
                                 max=self.resource.get_size()[1] - 1)
            self.sizer.Add(self.yCtrl, 0, flag=wx.ALIGN_BOTTOM)

            self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.xCtrl)
            self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.yCtrl)

        self.sizer.Add(self.toolbar, 0,
                       flag=wx.ALIGN_BOTTOM)
        self.SetSizerAndFit(self.sizer)

        self.Bind(wx.EVT_PAINT, self.OnPaint, self)

    def OnPaint(self, event):
        #Note a VERY misleading bug when the panel is too big for the place in
        #the AUINoteBook - the costume begins to stretch over borders etc.
        size = [i - 20 for i in self.GetSize()]  # 10px padding
        size[1] -= self.toolbar.GetSize()[1]

        image_prop = self.resource.get_size()
        ratio = min(size[0] / image_prop[0], size[1] / image_prop[1])

        image_size = [int(ratio * i) for i in image_prop]
        image_pos = ((size[0] - image_size[0]) / 2 + 10,
                     (size[1] - image_size[1]) / 2 + 10)

        if image_size[0] < 1 or image_size[1] < 1:
            return event.Skip()

        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        dc.DrawRectangle(image_pos[0] - 1, image_pos[1] - 1,
                         image_size[0] + 2, image_size[1] + 2)
        dc.DrawBitmap(self.resource.get_resized_image(image_size,
                                                  costume.FORMAT_BITMAP),
                      *image_pos)

        if self.costume:
            dc.DrawLine(ratio * self.xCtrl.GetValue() + image_pos[0],
                        0,
                        ratio * self.xCtrl.GetValue() + image_pos[0],
                        size[1] + 20)

            dc.DrawLine(0,
                        ratio * self.yCtrl.GetValue() + image_pos[1],
                        size[0] + 20,
                        ratio * self.yCtrl.GetValue() + image_pos[1])
        dc.EndDrawing()

        event.Skip()

    def OnCenter(self, event):
        self.xCtrl.SetValue(self.resource.get_size()[0] // 2)
        self.yCtrl.SetValue(self.resource.get_size()[1] // 2)
        self.OnSpin(event)

    @not_implemented
    def OnDuplicate(self, event):
        pass

    @not_implemented
    def OnEdit(self, event):
        pass

    def OnSpin(self, event):
        self.resource.set_center(self.xCtrl.GetValue(), self.yCtrl.GetValue())
        self.Refresh()


class LeftPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        runtime.leftPanel = self
        self.SetMinSize((480, 500))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        debug("Making notebook...", 1)
        self.noteBook = aui.AuiNotebook(self)
        welcome = wx.TextCtrl(self,
                            style=wx.TE_MULTILINE | wx.HSCROLL)
        welcome.write(welcome_text)
        welcome.SetFont(ScriptEditor.font)
        welcome.SetDefaultStyle(ScriptEditor.style)

        self.noteBook.AddPage(welcome, 'Welcome')
        self.welcomeOpen = True

        self.pages = []

        self.noteBook.SetMinSize((300, 450))
        debug("Done.", -1)
        self.sizer.Add(self.noteBook, 1, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)
        self.SetMinSize(self.GetSize())

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE,
                  self.OnPageClose, self.noteBook)
        #wxpython 2.9 compatibility
        if wx.VERSION[1] > 8:
            self.imageList = wx.ImageList(16, 16)
            self.noteBook.AssignImageList(self.imageList)


    def _NewPage(self, Window, title, bitmap, token):
        if self.welcomeOpen:
            self.noteBook.DeletePage(0)
            self.welcomeOpen = False
        try:
            self.noteBook.AddPage(Window, title, select=True, bitmap=bitmap)
        except TypeError:
            #API change on wxpython >= 2.9
            i = self.imageList.Add(bitmap)
            self.noteBook.AddPage(Window, title, select=True,
                                  imageId=self.imageList.GetImageCount() - 1)
            self.noteBook.SetPageImage(self.noteBook.GetPageCount() - 1, i)
        self.pages.append(token)

    def OpenScriptEditor(self, sprite):
        """OpenScriptEditor(sprite)

        Opens a new ScriptEditor tab for the given sprite.
        """
        if (sprite.name, SCRIPT) in self.pages:
            self.noteBook.SetSelection(self.pages.index((sprite.name, SCRIPT)))
            return
        self._NewPage(ScriptEditor(sprite, (sprite.name, SCRIPT), self.noteBook),
                      sprite.name, media.get_icon('script'),
                      (sprite.name, SCRIPT))

    def OpenImageEditor(self, sprite):
        """OpenImageEditor(sprite)

        Opens a new ScriptEditor tab for the given sprite.
        """
        if (sprite.name, IMAGE) in self.pages:
            self.noteBook.SetSelection(self.pages.index((sprite.name, IMAGE)))
            return
        self._NewPage(ImageEditor(sprite, self.noteBook),
                      sprite.name, media.get_icon('image'),
                      (sprite.name, IMAGE))

    @not_implemented
    def OpenSoundEditor(self, sprite):
        pass

    #Cleans self.imageList on wxpython >= 2.9
    def OnPageClose(self, event):
        if self.welcomeOpen:
            self.welcomeOpen = False
            return
        try:
            self.imageList.Remove(event.GetOldSelection())
        except AttributeError:
            pass
        self.pages.pop(event.GetOldSelection())

    def RemovePageByToken(self, token):
        index = self.pages.index(token)
        self.noteBook.DeletePage(index)

    def RefreshPages(self):
        debug('Deleting old pages...')
        try:
            old_selection = self.pages[self.noteBook.GetSelection()]
        #No open pages
        except IndexError:
            old_selection = None
        for _ in xrange(self.noteBook.GetPageCount()):
            self.noteBook.DeletePage(0)
        debug("Done.")
        
        debug("Recreating opened pages...")
        names = {sprite.name: sprite for sprite in
                 runtime.project.sprites + [runtime.project.stage]}
        functions = {SCRIPT: self.OpenScriptEditor,
                     IMAGE: self.OpenImageEditor,
                     SOUND: self.OpenSoundEditor}
        open_pages, self.pages = self.pages, []

        for name, type in open_pages:
            if name in names:
                functions[type](names[name])

        if old_selection in open_pages:
            self.noteBook.SetSelection(open_pages.index(old_selection))
        debug("Done.")
