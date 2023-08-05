from collections import OrderedDict
from weakref import WeakKeyDictionary, proxy
import wx
from M30W.debug import debug, not_implemented
from M30W import runtime
from M30W.sprites import rotmodes
import M30W.media as media
from wx.lib.mixins.listctrl import TextEditMixin, ListCtrlAutoWidthMixin


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
        except (TypeError, ValueError):
            self.listCtrl.SetStringItem(event.GetIndex(), 1,
                                        str(getattr(self.sprite, attr)))
            event.Veto()

    specials = {'draggable': lambda t: False if t == 'True' else True,
                'visible': lambda t: False if t == 'True' else True,
                'rotmode':
            lambda t: rotmodes[(rotmodes.index(t) + 1) % 3]}

    def AllowSizing(self):
        self.listCtrl._onResize = self.listCtrl._onResize_
        self.listCtrl._doResize = self.listCtrl._doResize_

    def DisableSizing(self):
        self.listCtrl._onResize = lambda: None
        self.listCtrl._doResize = lambda: None


class SpritePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        runtime.spritePanel = self

        debug("Making sprites listbook...")

        self.listBook = wx.Listbook(self, style=wx.LB_LEFT)
        self.il = wx.ImageList(32, 32)
        self.listBook.AssignImageList(self.il)
        #Stores refs to SpriteViewers and thumbnails
        self.last_update = WeakKeyDictionary()
        self.UpdateList()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnOpenScriptEditor,
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
        self.Bind(wx.EVT_MENU, self.OnExport,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE),
                                shortHelpString="Export Sprite"))
        self.Bind(wx.EVT_MENU, self.OnDelete,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                wx.ArtProvider_GetBitmap(wx.ART_CROSS_MARK),
                                shortHelpString="Delete Sprite"))
        self.Bind(wx.EVT_MENU, self.OnDown,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
                                wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN),
                                shortHelpString="Move Down"))
        self.Bind(wx.EVT_MENU, self.OnUp,
                  self.toolBar.AddSimpleTool(wx.ID_ANY,
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

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.listBook, 1, flag=wx.EXPAND)
        self.sizer.Add(self.toolBar, 0, flag=wx.EXPAND)
        self.SetSizerAndFit(self.sizer)

    @staticmethod
    def GetItems():
        return (runtime.get_stage(),) + runtime.get_sprites()

    @staticmethod
    def ShortenName(name, max_len):
        if len(name) < max_len: return name
        else: return name[:max_len - 3] + '...'

    #I tried to optimize it really hard - it still takes around 0.3 seconds
    #when you have about ~30 sprites, which is not the fastest :/
    def UpdateList(self, select=0):
        mapping = {}
        for sprite, (panel, thumbnail) in self.last_update.iteritems():
            mapping[sprite] = (panel, thumbnail)
            panel.DisableSizing()

        debug("Removing pages...")
        self.listBook.Freeze()
        while self.listBook.GetPageCount() != 0:
            self.listBook.RemovePage(0)
        self.il.RemoveAll()
        debug("Done.")

        for sprite in self.GetItems():
            if not sprite in mapping:
                mapping[sprite] = (SpriteViewer(self.listBook, sprite),
                            sprite.costumes[sprite.costume].get_thumbnail(32))
            self.il.Add(mapping[sprite][1])

            mapping[sprite][0].DisableSizing()
            self.listBook.AddPage(mapping[sprite][0],
                                  self.ShortenName(sprite.name, 10),
                                  imageId=self.il.GetImageCount() - 1
                                  )

        for sprite, (panel, thumbnail) in mapping.iteritems():
            self.last_update[sprite] = panel, thumbnail
            panel.AllowSizing()
        self.listBook.SetSelection(select)
        self.listBook.Thaw()

    @not_implemented
    def UpdateThumbnail(self, index):
        pass

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
        runtime.new()

    @not_implemented
    def OnOpen(self, event):
        pass

    @not_implemented
    def OnExport(self, event):
        pass

    def OnDelete(self, event):
        if self.listBook.GetSelection() == 0:
            return
        runtime.delete(self.listBook.GetSelection() - 1)

    def OnDown(self, event):
        if self.listBook.GetSelection() == self.listBook.GetPageCount() - 1:
            return
        runtime.movedown(self.listBook.GetSelection() - 1)

    def OnUp(self, event):
        if self.listBook.GetSelection() < 2:
            return
        runtime.moveup(self.listBook.GetSelection() - 1)
