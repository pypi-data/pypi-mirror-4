class Line(str):
    """Line(line, sprite, string) -> Line object

    For error handling support, this is basically a wrapper for the str type.
    You can get the original line of that code line using l.line."""
    def __new__(cls, line, sprite, string):
        obj = str.__new__(cls, string)
        obj.line = line
        obj.sprite = sprite
        return obj

    def __add__(self, other):
        return self.__class__(self.line, self.sprite, str(self)[:] + other)

    def __getslice__(self, i, j):
        return self.__class__(self.line, self.sprite,
                              str(self)[i:j])
