from .base import Base
from M30W.costume import Costume
from M30W.lists import ScratchList
try:
    import kurt
except ImportError:
    pass


NORMAL = 'normal'
RL = "leftRight"
NO = "none"


class Sprite(Base):
    kwords = Base.kwords.copy()
    kwords.update({'x': lambda: 0.0,
                   'y': lambda: 0.0,
                   'direction': lambda: 90.0,
                   'rotmode': lambda: NORMAL,
                   'draggable': lambda: False,
                   'size': lambda: 100.0,
                   'visible': lambda: True})

    def __init__(self, name, **kwargs):
        super(Sprite, self).__init__(name, **kwargs)

    @classmethod
    def from_kurt(cls, morph):
        costumes = [Costume.from_kurt(costume) for costume in morph.costumes]
        costume = morph.costumes.index(morph.costume)
        x, y, _, _ = morph.bounds.value
        y *= -1
        rx, ry = costumes[costume].get_center()
        x += rx - 240
        y += -ry + 180
        code = ("\n" * 3).join([script.to_block_plugin()
                                for script in morph.scripts])
        rotmode = morph.rotationStyle.value
        direction = (morph.rotationDegrees + 90.0) % 360
        if direction > 180: direction -= 360
        lists = {name: ScratchList(*list.items) for
                 name, list in morph.lists.iteritems()}
        return cls(morph.name,
                   costumes=costumes,
                   costume=costume,
                   code=code,
                   vars=morph.variables.copy(),
                   lists=lists,
                   volume=morph.volume,
                   x=x,
                   y=y,
                   direction=direction,
                   rotmode=rotmode,
                   draggable=morph.draggable,
                   size=morph.scalePoint.value[0] * 100,
                   visible=not morph.flags)


    def to_kurt(self):
        morph = kurt.Sprite()
        self.set_kurt_attrs(morph)
        morph.name = self.name
        morph.flags = 0 if self.visible else 1
        morph.rotationStyle = kurt.Symbol(self.rotmode)
        direction = self.direction
        if direction < 0: direction += 360
        direction = (direction - 90) % 360
        morph.rotationDegrees = direction
        morph.scalePoint = kurt.Point((self.size / 100,) * 2)
        rx, ry = self.costumes[self.costume].get_center()
        x1, y1 = self.x, self.y
        x1 -= rx - 240
        y1 += ry - 180
        y1 *= -1
        w, h = self.costumes[self.costume].get_size()
        x2, y2 = x1 + w, y1 + h
        morph.bounds = kurt.Rectangle([x1, y1, x2, y2])

        return morph

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = float(value)

    @property
    def pos(self):
        return '%s:%s' % (self.x, self.y)

    @pos.setter
    def pos(self, value):
        self.x, self.y = [float(x) for x in value.split(':')]

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = float(value)

    @property
    def rotmode(self):
        return self._rotmode

    @rotmode.setter
    def rotmode(self, value):
        if not value in (NORMAL, RL, NO):
            raise TypeError("Invalid mode!")
        self._rotmode = value

    @property
    def draggable(self):
        return self._draggable

    @draggable.setter
    def draggable(self, value):
        self._draggable = bool(value)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = float(value)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = bool(value)
