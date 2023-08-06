# This file is part of the M30W software.
# Copyright (C) 2012-2013 M30W developers.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import weakref, os, time, tempfile, subprocess, threading
import wx
from wx import aui
from M30W.debug import debug, not_implemented
from M30W import runtime, costume, media
from M30W.config import config
from dialogs import error

IMAGE = 'imageeditor'
SOUND = 'soundeditor'
SCRIPT = 'scripteditor'
MAX_NAME_LEN = 10

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
    # TODO: let the user config tab width (25 * chrs)

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
        # #Allows undo&redo
        # if time.time() - self.lastletter > 0.3:
            # self.undo.append(self.textCtrl.GetValue())
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


class ImageEditor(wx.Panel):
    def __init__(self, sprite, parent):
        wx.Panel.__init__(self, parent)

        self.listBook = wx.Listbook(self, style=wx.LB_LEFT)
        self.sprite = sprite
        self.il = wx.ImageList(32, 32)
        self.names = []
        self.listBook.AssignImageList(self.il)
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED,
                  self.OnItemFocused,
                  self.listBook.GetListView())

        self.toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL)

        self.Bind(wx.EVT_MENU, self.OnDown,
                  self.toolbar.AddSimpleTool(wx.ID_DOWN,
                                    wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN),
                                    shortHelpString="Move Down"))
        self.Bind(wx.EVT_MENU, self.OnUp,
                  self.toolbar.AddSimpleTool(wx.ID_UP,
                                    wx.ArtProvider_GetBitmap(wx.ART_GO_UP),
                                    shortHelpString="Move Up"))
        self.toolbar.AddSeparator()
        self.Bind(wx.EVT_MENU,
                  self.OnDelete,
                  self.toolbar.AddSimpleTool(wx.ID_DELETE,
                                    wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK),
                                    shortHelpString="Delete"))
        self.Bind(wx.EVT_MENU,
                  self.OnDuplicate,
                  self.toolbar.AddSimpleTool(wx.ID_ANY,
                                             media.get_icon('duplicate'),
                                             shortHelpString="Duplicate"))
        self.toolbar.AddSeparator()
        self.Bind(wx.EVT_MENU,
                  self.OnEdit,
                  self.toolbar.AddSimpleTool(wx.ID_EDIT,
                                             media.get_icon('edit'),
                                             shortHelpString="Edit"))
        self.Bind(wx.EVT_MENU,
                  self.OnRefresh,
                  self.toolbar.AddSimpleTool(wx.ID_REFRESH,
                                             media.get_icon('refresh'),
                                             shortHelpString="Refresh"))
        if not self.sprite.is_stage:
            self.toolbar.AddSeparator()
            self.Bind(wx.EVT_MENU,
                      self.OnCenter,
                      self.toolbar.AddSimpleTool(wx.ID_ANY,
                                                 media.get_icon('center'),
                                                 shortHelpString="Center"))      

        self.toolbar.Realize()

        # object because we imported costume
        self.UpdateList()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.listBook, 1, wx.EXPAND)
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.SetSizerAndFit(self.sizer)

    @staticmethod
    def ShortenName(name):
        if len(name) < MAX_NAME_LEN + 3: return name
        else: return name[:MAX_NAME_LEN - 3] + '...'

    def UpdateList(self):
        self.listBook.DeleteAllPages()
        for object in self.sprite.costumes:
            self.il.Add(object.get_thumbnail(32, costume.FORMAT_BITMAP))
            self.listBook.AddPage(ResourceViewer(self,
                                                 object,
                                                 not self.sprite.is_stage),
                         self.ShortenName(object.name),
                         select=True,
                         imageId=self.il.GetImageCount() - 1
                         )
        self.listBook.SetSelection(self.sprite.costume)

    def OnUp(self, event):
        index = self.listBook.GetSelection()
        costumes = self.sprite.costumes
        page = self.listBook.GetPage(index)
        self.listBook.RemovePage(index)
        name = self.ShortenName(costumes[index].name)
        self.listBook.InsertPage(index - 1, page, name, select=True,
                                 imageId=index)
        (costumes[index - 1], costumes[index]) = (costumes[index],
                                                  costumes[index - 1])

    def OnDown(self, event):
        index = self.listBook.GetSelection()
        costumes = self.sprite.costumes
        page = self.listBook.GetPage(index)
        self.listBook.RemovePage(index)
        name = self.ShortenName(costumes[index].name)
        self.listBook.InsertPage(index + 1, page, name, select=True,
                                 imageId=index)
        (costumes[index], costumes[index + 1]) = (costumes[index + 1],
                                                  costumes[index])
        print costumes

    def OnItemFocused(self, event):
        self.toolbar.EnableTool(wx.ID_DELETE, len(self.sprite.costumes) > 1)
        self.toolbar.EnableTool(wx.ID_UP, event.GetIndex() != 0)
        self.toolbar.EnableTool(wx.ID_DOWN,
                            event.GetIndex() < len(self.sprite.costumes) - 1)

    def OnDuplicate(self, event):
        selection = self.listBook.GetSelection()
        costume = self.sprite.costumes[selection].duplicate()
        names = map(lambda a: a.name, self.sprite.costumes)
        while (costume.name in names):
            costume = costume.duplicate()
        self.sprite.costumes.insert(selection + 1, costume)
        wx.CallAfter(self.UpdateList)

    def OnDelete(self, event):
        selection = self.listBook.GetSelection()
        self.sprite.costumes.pop(selection)
        self.listBook.DeletePage(selection)

    def OnEdit(self, event):
        selection = self.listBook.GetSelection()
        if config['IMAGE_EDITOR_PATH']:
            path = os.path.join(tempfile.gettempdir(),
                                '%s.png' % id(self.sprite.costumes[selection]))
            self.sprite.costumes[selection].save_to(path)
            subprocess.Popen([config['IMAGE_EDITOR_PATH'], path])
        else:
            error("Please configure editor!",
                  "You must configure your favorite image editor "
                  "befor using this feature!")

    def OnRefresh(self, event):
        selection = self.listBook.GetSelection()
        path = os.path.join(tempfile.gettempdir(),
                       '%s.png' % id(self.sprite.costumes[selection]))
        if os.path.isfile(path):
            self.sprite.costumes[selection].load_from(path)
        else:
            return
        def refresh():
            runtime.stage.Refresh()
            self.UpdateList()
            runtime.spritePanel.UpdateThumbnail(0 if self.sprite.is_stage
                                else runtime.get_sprites().index(self.sprite))
        wx.CallAfter(refresh)

    def OnCenter(self, event):
        self.listBook.GetCurrentPage().Center()
 
class ResourceViewer(wx.Panel):
    def __init__(self, parent, resource, show_grid=True):
        wx.Panel.__init__(self, parent, style=wx.FULL_REPAINT_ON_RESIZE)
        self.resource = weakref.proxy(resource)
        self.show_grid = show_grid

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        if self.show_grid:
            self.sizer.AddSpacer(10, 10)
            self.xText = wx.StaticText(self, wx.ID_ANY, label="X:")
            self.sizer.Add(self.xText, 0, border=5,
                           flag=wx.ALIGN_BOTTOM | wx.BOTTOM)

            self.xCtrl = wx.SpinCtrl(self,
                                 wx.ID_ANY,
                                 initial=self.resource.center[0],
                                 min=0,
                                 max=self.resource.size[0] - 1)
            self.sizer.Add(self.xCtrl, 0, flag=wx.ALIGN_BOTTOM)

            self.sizer.AddSpacer(5, 5)

            self.yText = wx.StaticText(self, wx.ID_ANY, label="Y:")
            self.sizer.Add(self.yText, 0, border=5,
                           flag=wx.ALIGN_BOTTOM | wx.BOTTOM)

            self.yCtrl = wx.SpinCtrl(self,
                                 wx.ID_ANY,
                                 initial=self.resource.center[1],
                                 min=0,
                                 max=self.resource.size[1] - 1)
            self.sizer.Add(self.yCtrl, 0, flag=wx.ALIGN_BOTTOM)

            self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.xCtrl)
            self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.yCtrl)

        self.SetSizerAndFit(self.sizer)

        self.Bind(wx.EVT_PAINT, self.OnPaint, self)

    def OnPaint(self, event):
        # Note a VERY misleading bug when the panel is too big for the place in
        # the AUINoteBook - the costume begins to stretch over borders etc.
        size = [i - 20 for i in self.GetSize()]  # 10px padding
        size[1] -= 25 # Costume name
        if self.show_grid:
            size[1] -= self.xCtrl.GetSize()[1]

        image_prop = self.resource.size
        ratio = min(size[0] / image_prop[0], size[1] / image_prop[1])

        image_size = [int(ratio * i) for i in image_prop]
        image_pos = ((size[0] - image_size[0]) / 2 + 10,
                     (size[1] - image_size[1]) / 2 + 35)

        if image_size[0] < 1 or image_size[1] < 1:
            return event.Skip()

        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        font = wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(font)
        extent = dc.GetTextExtent(self.resource.name)
        dc.DrawText(self.resource.name,
                    (size[0] - extent[0] + 20) // 2,
                    10)
        dc.DrawRectangle(image_pos[0] - 1, image_pos[1] - 1,
                         image_size[0] + 2, image_size[1] + 2)
        dc.DrawBitmap(self.resource.get_resized_image(image_size,
                                                  costume.FORMAT_BITMAP),
                      *image_pos)

        if self.show_grid:
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

    def Center(self):
        self.xCtrl.SetValue(self.resource.size[0] // 2)
        self.yCtrl.SetValue(self.resource.size[1] // 2)
        self.OnSpin(None)

    def OnSpin(self, event):
        self.resource.center = self.xCtrl.GetValue(), self.yCtrl.GetValue()
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
        # wxpython 2.9 compatibility
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
            # API change on wxpython >= 2.9
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

    # Cleans self.imageList on wxpython >= 2.9
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
        # No open pages
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
