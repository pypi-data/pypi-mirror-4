"""Module providing simple debug tools
"""
import sys
import inspect
try:
    import kurt
except ImportError:
    kurt = None

DEBUG = '--debug' in sys.argv
_INDENT = 0


def debug(message, indent=0):
    """debug(message, indent=0)

    Prints message to stdout if --debug flag is on.
    Use indent to indicate opening and closing of tasks."""
    if not DEBUG: return
    global _INDENT
    if indent and indent < 0:
        _INDENT += indent
    print '\t' * _INDENT,
    print message
    if indent and indent > 0:
        _INDENT += indent


not_implemented_functions = []
class not_implemented():
    def __init__(self, func):
        self.func = func
        not_implemented_functions.append(func)

    def __call__(self, *args, **kwargs):
        print ("Called function %s in file %s which is yet not implemented."
               % (self.func.__name__, inspect.getsourcefile(self.func)))


class NoKurt(Exception):
    def __init__(self):
        Exception.__init__(self, "Saving or loading of .sb files isn't "
                                 "working without kurt. Please install it "
                                 "if you want to do so!")
def ensure_kurt():
    """
    Ensures kurt is available on system, raises error if not.
    """
    if not kurt:
        raise NoKurt

def print_not_implemented_functions():
    for func in not_implemented_functions:
        print "function %s in file %s" % (func.__name__,
                                          inspect.getsourcefile(func))


if __name__ == '__main__':
    print """M30W debug tools, released under GPL3.
Copyright (C) 2012 M30W developers.\n"""
    debug("Debugging...")
