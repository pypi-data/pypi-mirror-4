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

import time
from M30W.debug import debug, not_implemented
try:
    import kurt
except ImportError:
    pass

class Base(object):
    kwords = {'costumes': lambda: [],
              'costume': lambda: 0,
              'code': lambda: "",
              'vars': lambda: {},
              'lists': lambda: {},
              'volume': lambda: 100}

    def __init__(self, name, **kwargs):
        """Base(self, name, costumes=[], costume=0, code="", vars={}, lists={},
                volume=100)

        :Parameters:
        - `name`, `costumes`,`costume`, `code`, `vars`,
          `lists`, `volume`
        """
        debug("Creating sprite %s" % name)
        self._name = name

        # Functions because shared mutable objects
        for kword in self.kwords:
            if kword in kwargs: setattr(self, '_' + kword, kwargs[kword])
            else: setattr(self, '_' + kword, self.kwords[kword]())

        self._sounds_backup = kwargs['sounds'] if 'sounds' in kwargs else None

    def __repr__(self):
        return "<Sprite '%s' at %s>" % (self.name, id(self))

    @classmethod
    def from_kurt(cls, morph):
        raise NotImplementedError

    def to_kurt(self):
        raise NotImplementedError
    
    #Called from children, to reduce code be rewritten.
    def set_kurt_attrs(self, morph):
        morph.images = [costume.to_kurt() for costume in self._costumes]
        morph.costume = morph.images[self._costume]
        lists = {}
        for name, list in self._lists.iteritems():
            lists[name] = kurt.ScratchListMorph(name=name, items=list)
        morph.lists = lists
        morph.vars = self._vars.copy()  # I don't trust kurt :)
        morph.volume = self._volume

        if self._sounds_backup:
            morph.sounds = self._sounds_backup

        code = unicode(self.code).split('\n' * 3)
        code = [i for i in code if i.strip("\r\n ")]
        for sheet in code:
            sheet = kurt.parse_block_plugin(sheet)
            sheet.morph = morph
            sheet.pos = kurt.Point([20, 20])
            morph.scripts.extend([sheet])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def vars(self):
        return self._vars

    @property
    def lists(self):
        return self._lists

    @property
    def costumes(self):
        return self._costumes

    @property
    def costume(self):
        return self._costume

    @costume.setter
    def costume(self, value):
        self.costumes[value]  # Validate that index is in range
        self._custume = value

    @property
    def active_costume(self):
        return self.costumes[self.costume]

    @active_costume.setter
    def active_costume(self, value):
        self.costume = self.costumes.index(value)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        value = float(value)
        if not 0 <= value <= 100:
            print value
            raise TypeError("Value must bew in range 0-100")
        self._volume = value

    @property
    def is_stage(self):
        return self.name == 'Stage'

    # Sounds support comes later.

    #==========================================================================
    # Begin blocks code
    #==========================================================================
    @not_implemented
    def forever(self, args, cargs):
        pass

    @not_implemented
    def repeat(self, args, cargs):
        pass

    @not_implemented
    def dountil(self, args, crags):
        pass

    @not_implemented
    def doif(self, args, cargs):
        pass

    @not_implemented
    def doifelse(self, args, crags):
        pass

    def wait(self, args):
        exec_time = time.time()
        while not exec_time - time.time() > args[0]:
            yield

    @not_implemented
    def waituntil(self, args):
        pass
