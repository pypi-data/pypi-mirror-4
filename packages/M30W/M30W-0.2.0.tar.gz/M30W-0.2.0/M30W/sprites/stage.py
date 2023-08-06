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

from .base import Base
from M30W.costume import Costume, get_default_background
from M30W.lists import ScratchList
try:
    import kurt
except ImportError:
    pass


class Stage(Base):
    kwords = Base.kwords.copy()
    kwords.update({'tempo': lambda: 60})

    def __init__(self, **kwargs):
        """Stage(self, costumes=[], costume=0, code="", vars={}, lists={},
                volume=100, tempo=60)

        :Parameters:
        - `costumes`,`costume`, `code`, `vars`, `lists`, `volume`, `tempo`
        """
        Base.__init__(self, 'Stage', **kwargs)

        if not self.costumes:
            self.costumes.append(get_default_background())

    @classmethod
    def from_kurt(cls, morph):
        code = ("\n" * 3).join([script.to_block_plugin()
                                    for script in morph.scripts])

        costumes = [Costume.from_kurt(costume) for
                    costume in morph.backgrounds]
        costume = morph.backgrounds.index(morph.background)

        lists = {name: ScratchList(*list.items) for
                 name, list in morph.lists.iteritems()}

        if morph.sounds:
            sounds = morph.sounds
        else:
            sounds = None

        return cls(costumes=costumes,
                   costume=costume,
                   code=code,
                   vars=morph.variables.copy(),
                   lists=lists,
                   volume=morph.volume,
                   tempo=morph.tempoBPM,
                   sounds=sounds)


    def to_kurt(self):
        morph = kurt.Stage()
        self.set_kurt_attrs(morph)
        morph.tempoBPM = self._tempo
        return morph

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        self._tempo = value
