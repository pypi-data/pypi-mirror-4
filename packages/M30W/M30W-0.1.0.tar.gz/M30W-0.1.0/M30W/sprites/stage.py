from .base import Base
from M30W.costume import Costume
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
