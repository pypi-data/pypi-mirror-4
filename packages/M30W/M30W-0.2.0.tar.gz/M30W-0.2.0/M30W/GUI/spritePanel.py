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

from collections import OrderedDict
from weakref import WeakKeyDictionary, proxy
import wx, dialogs
from M30W.debug import debug, not_implemented
from M30W import runtime
from M30W.sprites import rotmodes
import M30W.media as media
from wx.lib.mixins.listctrl import TextEditMixin, ListCtrlAutoWidthMixin

MAX_NAME_LEN = 10

class EditableListCtrl(wx.ListCtrl, TextEditMixin, ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        TextEditMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        self._onResize_ = self._onResize
        self._doResize_ = self._doResize


class SpriteViewer(wx.Panel):
    sprite_attr = OrderedDict((('Name', 'name'),
              ('Position', 'pos'),
              ('Rotation', 'rotmode'),
              ('Direction', 'direction'),
              ('Draggable', 'draggable'),
              ('Visible', 'visible'),
              ('Volume', 'volume')))
    stage_attr = OrderedDict((('Name', 'name'),
             ('Volume', 'volume'),
             ('Tempo (BPM)', 'tempo')))

    def __init__(self, parent, sprite):
        super(SpriteViewer, self).__init__(parent)
        self.sprite = proxy(sprite, lambda proxy: self.Destroy())

        self.listCtrl = EditableListCtrl(self, style=wx.LC_REPORT |
                                wx.LC_NO_HEADER | wx.LC_VRULES | wx.LC_HRULES)
        self.listCtrl.InsertColumn(0, 'property')
        self.listCtrl.InsertColumn(1, 'value')
        if self.sprite.name == 'Stage':
            self.sprite_attr = self.stage_attr
        for label, attr in self.sprite_attr.iteritems():
            self.listCtrl.Append((label, getattr(self.sprite, attr)))
        self.listCtrl.SetColumnWidth(0, -1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.listCtrl, 1, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)

        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit,
                  self.listCtrl)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndLabelEdit,
                  self.listCtrl)

    def __repr__(self):
        return '<SpriteViewer for sprite "%s" at %s>' % (self.sprite.name,
                                                         id(self))

    def OnBeginLabelEdit(self, event):
        event.Allow()
        attr = self.sprite_attr[self.listCtrl.GetItem(event.GetIndex(),
                                                      0).GetText()]
        if event.m_col == 0: event.Veto()
        #Don't let Stage get renamed
        if self.sprite.name == 'Stage' and attr == 'name':
            event.Veto()
        if attr in self.specials:
            self.listCtrl.SetStringItem(event.GetIndex(), 1,
                                    str(self.specials[attr](event.GetLabel())))
            setattr(self.sprite, attr, self.specials[attr](event.GetLabel()))
            event.Veto()


    def OnEndLabelEdit(self, event):
        attr = self.sprite_attr[self.listCtrl.GetItem(event.GetIndex(),
                                                      0).GetText()]
        value = event.GetLabel()
        try:
            setattr(self.sprite, attr, value)
            self.listCtrl.SetStringItem(event.GetIndex(), 1,
                                        getattr(self.sprite, attr))
            if attr == 'name':
                wx.CallAfter(runtime.spritePanel.UpdateList)
        except (TypeError, ValueError):
            self.listCtrl.SetStringItem(event.GetIndex(), 1,
                                        str(getattr(self.sprite, attr)))
            event.Veto()

    specials = {'draggable': lambda t: False if t == 'True' else True,
                'visible': lambda t: False if t == 'True' else True,
                'rotmode':
            lambda t: rotmodes[(rotmodes.index(t) + 1) % 3]}


class SpritePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        runtime.spritePanel = self

        debug("Making sprites listbook...", 1)

        self.listBook = wx.Listbook(self, style=wx.LB_LEFT)
        self.il = wx.ImageList(32, 32)
        self.listBook.AssignImageList(self.il)
        #Stores refs to SpriteViewers and thumbnails
        self.last_update = WeakKeyDictionary()

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnOpenScriptEditor,
                  self.listBook.GetListView())

        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnItemFocused,
                  self.listBook.GetListView())

        debug("Done.")

        debug("Making Toolbar...")
        self.toolBar = wx.ToolBar(self, style=wx.TB_HORIZONTAL)
        self.Bind(wx.EVT_MENU, self.OnNew,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                wx.ArtProvider_GetBitmap(wx.ART_NEW),
                                shortHelpString="Make New Sprite"))
        self.Bind(wx.EVT_MENU, self.OnOpen,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN),
                                shortHelpString="New Sprite From File"))
        wx.ID_EXPORT = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnExport,
                  self.toolBar.AddSimpleTool(wx.ID_EXPORT,
                                wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE),
                                shortHelpString="Export Sprite"))
        self.Bind(wx.EVT_MENU, self.OnDelete,
                  self.toolBar.AddSimpleTool(wx.ID_DELETE,
                                wx.ArtProvider_GetBitmap(wx.ART_CROSS_MARK),
                                shortHelpString="Delete Sprite"))
        self.Bind(wx.EVT_MENU, self.OnDown,
                  self.toolBar.AddSimpleTool(wx.ID_DOWN,
                                wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN),
                                shortHelpString="Move Down"))
        self.Bind(wx.EVT_MENU, self.OnUp,
                  self.toolBar.AddSimpleTool(wx.ID_UP,
                                wx.ArtProvider_GetBitmap(wx.ART_GO_UP),
                                shortHelpString="Move Up"))

        self.toolBar.AddSeparator()

        self.Bind(wx.EVT_MENU,
                  self.OnOpenScriptEditor,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                             media.get_icon('script'),
                                             shortHelpString="Edit Scripts"))
        self.Bind(wx.EVT_MENU,
                  self.OnOpenImageEditor,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                             media.get_icon('image'),
                                             shortHelpString="Edit Costumes"))
        self.Bind(wx.EVT_MENU,
                  self.OnOpenSoundEditor,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                             media.get_icon('sound'),
                                             shortHelpString="Edit Sounds"))

        self.toolBar.Realize()
        debug("Done.")

        #Is here out of context, but is necessary so the up/down buttons
        #are disabled.
        self.UpdateList()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.listBook, 1, flag=wx.EXPAND)
        self.sizer.Add(self.toolBar, 0, flag=wx.EXPAND)
        self.SetSizerAndFit(self.sizer)

    @staticmethod
    def GetItems():
        return [runtime.get_stage()] + runtime.get_sprites()

    @staticmethod
    def ShortenName(name):
        if len(name) < MAX_NAME_LEN: return name
        else: return name[:MAX_NAME_LEN - 3] + '...'

    def UpdateList(self, select=0):
        self.listBook.DeleteAllPages()

        debug("Creating new pages and putting them in...")
        for sprite in self.GetItems():
            self.il.Add(sprite.costumes[sprite.costume].get_thumbnail(32))
            self.listBook.AddPage(SpriteViewer(self.listBook, sprite),
                                  self.ShortenName(sprite.name),
                                  imageId=self.il.GetImageCount() - 1)
        debug("Done.")

    def UpdateThumbnail(self, index):
        sprite = self.GetItems()[index]
        self.il.Replace(index,
                        sprite.costumes[sprite.costume].get_thumbnail(32))

    def OnItemFocused(self, event):
        self.toolBar.EnableTool(wx.ID_UP,
                                event.GetIndex() >= 2)
        self.toolBar.EnableTool(wx.ID_DOWN,
                event.GetIndex() != 0 and
                event.GetIndex() < len(runtime.get_sprites()))
        self.toolBar.EnableTool(wx.ID_DELETE,
                event.GetIndex() != 0)
        self.toolBar.EnableTool(wx.ID_EXPORT,
                event.GetIndex() != 0)

    def OnOpenScriptEditor(self, event):
        runtime.leftPanel.OpenScriptEditor(
                            self.GetItems()[self.listBook.GetSelection()])

    def OnOpenImageEditor(self, event):
        runtime.leftPanel.OpenImageEditor(
                            self.GetItems()[self.listBook.GetSelection()])

    @not_implemented
    def OnOpenSoundEditor(self, event):
        pass

    def OnNew(self, event):
        sprite = runtime.new()
        self.il.Add(sprite.costumes[sprite.costume].get_thumbnail(32))
        self.listBook.AddPage(SpriteViewer(self.listBook, sprite),
                              self.ShortenName(sprite.name),
                              select=True,
                              imageId=self.il.GetImageCount() - 1)

    def OnOpen(self, event):
        path = dialogs.save("Please choose a sprite:",
                            "Scratch sprite files (*.sprite)|*.sprite|"
                            "All Files (*.*)|*.*")
        if path:
            runtime.project.new_sprite_from(path)

    def OnExport(self, event):
        path = dialogs.save("Please choose a sprite:",
                            "Scratch sprite files (*.sprite)|*.sprite|"
                            "All Files (*.*)|*.*")
        if path:
            sprite = runtime.project.sprites[self.listBook.GetSelection() - 1]
            sprite.save_to(path)

    def OnDelete(self, event):
        index = self.listBook.GetSelection()
        self.listBook.DeletePage(index)
        runtime.delete(index - 1)

    def OnDown(self, event):
        index = self.listBook.GetSelection()
        sprites = runtime.get_sprites()
        page = self.listBook.GetPage(index)
        self.listBook.RemovePage(index)
        #index + 1 because we have the stage also...
        name = self.ShortenName(runtime.get_sprites()[index - 1].name)
        self.listBook.InsertPage(index + 1, page, name, select=True,
                                 imageId=index)
        (sprites[index], sprites[index - 1]) = (sprites[index - 1],
                                                sprites[index])

    def OnUp(self, event):
        index = self.listBook.GetSelection()
        sprites = runtime.get_sprites()
        page = self.listBook.GetPage(index)
        self.listBook.RemovePage(index)
        #index + 1 because we have the stage also...
        name = self.ShortenName(runtime.get_sprites()[index - 1].name)
        self.listBook.InsertPage(index - 1, page, name, select=True,
                                 imageId=index)
        (sprites[index - 2], sprites[index - 1]) = (sprites[index - 1],
                                                    sprites[index - 2])
