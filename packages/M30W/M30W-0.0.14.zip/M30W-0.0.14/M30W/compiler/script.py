import re
from block import Block
from line import Line


def cleanup(code, sprite):
    """cleanup(code, sprite) -> cleaned up code

    Clean up a list of lines from comments etc."""
    #Not implemented in-line comments yet...
    code = [Line(index, sprite, line) for index, line
            in enumerate(code)
            if type(line) != Line]

    code = filter(lambda s: bool(s.replace(' ', '')), code)
    code = filter(lambda s: not s.replace(' ', '').startswith('#'), code)
    return code


class Script():
    def __init__(self, sprite, sourcecode, docleanup=True):
        """__init__(sprite, list of code lines) -> Script object

        Makes a new instance of Script object and compiles the script.
        You have to bind the script to an event using the executer module.
        """
        self.sprite = sprite

        self.code = sourcecode
        if docleanup:
            self.code = cleanup(self.code, self.sprite)

        def totree(code):
            copy = code[:] + ['']
            pattern = r'( *)'
            codeblock = []

            i = 0
            while i < len(copy):
                line = copy[i]
                #Using re group to find if it's deeper...
                if len(re.match(pattern, line).group(0)) > 0:
                    codeblock.append(copy.pop(i))
                else:
                    if codeblock:
                        copy.insert(i,
                                    Script(self.sprite,
                                           [line[4:] for line in codeblock],
                                    docleanup=False))
                        codeblock = []
                    i += 1
            return copy[:-1]

        self.code = totree(self.code)

        #Putting multiple C blocks of the same block together.
        for index, line in enumerate(self.code[:-3]):
            if (line.__class__ is Line and
                self.code[index + 1].__class__ is Script and
                self.code[index + 2].__class__ is Line and
                self.code[index + 3].__class__ is Script):
                if self.code[index + 2].startswith('\\'):
                    self.code[index] = (line + ' {script} ' +
                                   self.code.pop(index + 2)[1:])

        #Modifying the specs before c blocks to 'spec {script}' so they can
        #matched using re.
        for index, line in enumerate(self.code[:-1]):
            if type(line) is Line and self.code[index + 1].__class__ is Script:
                self.code[index] += ' {script}'

        self.sourcecode = self.code[:]

        #Converting Lines to Blocks.
        for index, line in enumerate(self.code):
            if line.__class__ == Script:
                continue
            cargs = []
            for i in range(index + 1, len(self.code)):
                if self.code[i].__class__ == Script:
                    cargs.append(self.code[i])
                else:
                    break
            self.code[index] = Block(line, cargs)

    def execute(self):
        """execute()

        Execute this script. This is actually executing it, not queuing it up.
        Returns when the script stops to run, not at all if it doesn't.
        """
        for block in self.code:
            block.execute()

    def print_code(self, code=None, indent=0):
        """print_code()

        Prints the sourcecode."""
        if not code:
            code = self.sourcecode

        printed_c = False
        for line in code:
            if line.__class__ == Script:
                if printed_c:
                    print ''
                line.print_code(indent=indent + 1)
                printed_c = True
            else:
                print indent * '\t' + line
                printed_c = False


if __name__ == '__main__':
    print '-' * 80 + "\nScript parsing test:\n"
    script = Script(None, r"""move 12 steps
forever
    if [1 > 2]
        say [32 + 32]
    \else
    # This is a comment.
    # In-line do not work (no idea how to check if it's inside
    # line or not, asking on AT)
        if ['42' = '42']
            say 'one is not bigger than two'
    repeat 4
        say 'That\'s a test'
""".split('\n'))
    script.print_code()
    print '-' * 80 + "\nLine objects test:\n"
    a = Line(42, 'a sprite', 'spam spam spam')
    print a, a.line, a.sprite, a.__class__
    b = a + ' eggs'
    print b, b.line, b.sprite, b.__class__
