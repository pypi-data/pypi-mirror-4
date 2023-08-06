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
