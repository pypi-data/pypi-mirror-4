import re


class Spec():
    """This class provides a OOP interface to parsing blocks.

    Spec arguments are:
    %s    is string, like in 'say %s'
    %n    is number, like in '%n + %n'
    %b    is boolean, like in 'wait until %b'
          because you can't really put inputs inside it,
          it accepts only nested reporters
    %c    is a c block, like in 'forever %c'
    %m    stands for many, because it accepts numbers as
          well as strings like in '%m > %m'.
          It is made because while in GUI there's no
          difference between number and string writing,
          in M30W you have to either write numbers as is
          or put strings inside apostrophes
    """
    args = {letter: '(' + pattern + '|\[.*\])' for letter, pattern in
            {'%s': r"'.*(?<!\\)'",
            '%n': r'\-?[0-9.]+',
            '%c': r'{script}',
            '%b': r'\[.*\]', # Because it can only match nested blocks.
            '%m': r"\-?[0-9.]+|'.*(?<!\\)'"}.items()}

    def __init__(self, spec, handler):
        """__init___(spec, handler) -> Spec object

        Creates new Spec object"""
        self.spec = re.escape(spec)  # Escaping characters
        self.spec = self.spec.replace('\\%', '%')  # We don't need them escaped
        self.handler = handler
        #Allows multiple whitespace characters
        #self.spec = self.spec.replace(' ', '\s+')  # Breaks up the matching :/
        #Replacing %(input) with equivalent re pattern
        for letter, pattern in self.args.items():
            self.spec = self.spec.replace(letter, pattern)

    def matches(self, key):
        """match(key) -> bool

        Check if the key matches one of the block specs."""
        return bool(re.match(self.spec, key))

    def handler(self):
        """handler() -> string

        Get the block handler as a string."""
        return self.handler

    def get_args(self, code):
        """get_args(code) -> list

        Returns the arguments that were caught using regex."""
        from M30W.compiler import Block  # Because of recursive imports.
        args = list(re.match(self.spec, code).groups())
        for index, arg in enumerate(args):
            if arg[0] + arg[-1] == '[]':
                args[index] = Block(arg[1:-1], [])
            if arg[0] + arg[-1] == "''":
                args[index] = arg[1:-1].replace("\\'", "'")
        return args

from specshandler import specs


def get_spec(key):
    for spec in specs:
        if spec.matches(key):
            return spec
    return None
