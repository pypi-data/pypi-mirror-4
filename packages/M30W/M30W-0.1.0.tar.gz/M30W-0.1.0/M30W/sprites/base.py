import time
from M30W.debug import debug, not_implemented
from M30W.costume import DEFAULT_COSTUME
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

        if not self.costumes:
            self.costumes.append(DEFAULT_COSTUME)

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
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        value = float(value)
        if not 0 <= value <= 100:
            print value
            raise TypeError("Value must bew in range 0-100")
        self._volume = value


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
