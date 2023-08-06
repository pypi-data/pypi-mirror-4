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

"""
Project class - stores sprites, project infos etc.
"""
import cPickle as pickle
from hashlib import sha256
from M30W import sprites
from M30W.debug import debug, not_implemented, ensure_kurt
try:
    import kurt
    from M30W.costume import _convert, FORMAT_PIL
except ImportError:
    kurt = None


class NoSavePath(Exception): pass


class Project(object):
    kwords = {'sprites': lambda: [],
              'stage': sprites.Stage,
              'author': lambda: u'',
              'comment': lambda: u'',
              'path': lambda: None}

    def __init__(self, **kwargs):
        for kword in self.kwords:
            if kword in kwargs: setattr(self, '_' + kword, kwargs[kword])
            else: setattr(self, '_' + kword, self.kwords[kword]())

        self.last_save = sha256(pickle.dumps(self, protocol=2)).hexdigest()

    def __getstate__(self):
        dict = self.__dict__.copy()
        dict.pop('last_save', None)
        return dict

    def __setstate__(self, dict):
        self.__dict__ = dict
        self.last_save = sha256(pickle.dumps(self, protocol=2)).hexdigest()

    @classmethod
    def from_kurt(cls, morph):
        stage = sprites.Stage.from_kurt(morph.stage)
        #Redefining sprites from outer scope...
        
        sprite = [sprites.Sprite.from_kurt(i) for i in morph.stage.sprites]
        author = morph.info['author']
        comment = morph.info['comment']
        path = morph.path
        return cls(stage=stage,
                   sprites=sprite,
                   author=author,
                   comment=comment,
                   path=path)

    def to_kurt(self):
        morph = kurt.ScratchProjectFile(self.path, load=False)
        morph.stage = self.stage.to_kurt()
        morph.sprites = [sprite.to_kurt() for sprite in self.sprites]
        for sprite in morph.sprites:
            for script in sprite.scripts:
                script.replace_sprite_refs(morph.get_sprite)
        from M30W import runtime
        thumbnail = _convert(runtime.stage.GetBitmap(), FORMAT_PIL)
        thumbnail = thumbnail.resize((160, 120))

        #We don't need the name, so we leave it empty
        morph.thumbnail = kurt.Image.from_image("", thumbnail)
        morph.info['author'] = self.author
        morph.info['comment'] = self.comment
        return morph

    @classmethod
    @not_implemented
    def from_sb2(cls, obj):
        pass

    @not_implemented
    def to_sb2(self):
        pass

    def save(self):
        debug("Saving project to %s" % self.path, 1)
        if self.path.endswith('.sb2'):
            raise NotImplementedError
        elif self.path.endswith('.m30w'):
            pickle.dump(self, open(self.path, 'wb'), protocol=2)
        #Change default to .sb2 when Scratch comes out?
        else:
            ensure_kurt()
            self.to_kurt().save()
        #So we can detect changes
        self.last_save = sha256(pickle.dumps(self, protocol=2)).hexdigest()
        debug("Done.", -1)

    def load(self):
        debug("Loading project from %s" % self.path, 1)
        if not self.path:
            raise ValueError("Project not saved yet!")
        if self.path.endswith('.sb2'):
            raise NotImplementedError
        elif self.path.endswith('.m30w'):
            project = pickle.load(self, open(self.path, 'wb'), protocol=2)
            self.__dict__ = Project.from_kurt(project).__dict__
        #Change default to .sb2 when Scratch comes out?
        else:
            ensure_kurt()
            project = kurt.ScratchProjectFile(self.path)
            self.__dict__ = Project.from_kurt(project).__dict__
        debug("Done.", -1)

    def new_sprite_from(self, path):
        ensure_kurt()
        file = kurt.ScratchSpriteFile(path)
        self.sprites.append(sprites.Sprite.from_kurt(file.sprite))

    @property
    def changed(self):
        current = sha256(pickle.dumps(self, protocol=2)).hexdigest()
        return self.last_save != current

    @changed.setter
    def changed(self, changed):
        if changed:
            self.last_save = ""
        else:
            self.last_save = sha256(pickle.dumps(self, protocol=2)).hexdigest()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def sprites(self):
        return self._sprites

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, value):
        assert isinstance(value, sprites.Stage)
        self._stage = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = unicode(value)

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = unicode(value)
