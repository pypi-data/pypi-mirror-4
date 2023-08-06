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

"""Provides global user settings.

:Usage:
- config: a dictionary, stores all config informations
- save(): forces save of the configurations to the disk
"""
import sys
import os
from json import load, dump


PATH = {'win32': lambda:
            os.path.join(os.environ['APPDATA'], 'M30W', 'M30W.json'),
        'cygwin': lambda: 
            os.path.join(os.environ['APPDATA'], 'M30W', 'M30W.json'),
        'linux2': lambda: os.path.expanduser('~/.config/M30W/M30W.json'),
        'darwin': lambda:
            os.path.expanduser('~/Library/Application Support/M30W/M30W.json')
        }[sys.platform]()

if not os.path.exists(PATH):
    try:
        if not os.path.isdir(os.path.dirname(PATH)):
            os.mkdir(os.path.dirname(PATH))
        open(PATH, 'w')
    except (OSError, IOError):
        raise SystemExit("Could not create config file at path '%s'" % PATH)

try:
    config = load(open(PATH))
except ValueError:
    config = {}

def save():
    """save()

    Saves configurations to the config file.
    """
    dump(config, open(PATH, 'w'))
