"""Provides global user settings.

:Usage:
- get_option(option, default, do_eval=False)
    Returns the value of the option specified. If non-existent returns
    default and assigns new option to it. If eval is True it returns
    evaluated answer (e.g. tuple, int, etc.)
- set_option(option, value): Sets the option specified to the value
- get_boolean(option, default):
- del_option(option): Deletes the option from the file
- save(): forces save of the configurations to the disk
"""
import sys
import os
from ConfigParser import RawConfigParser as Parser, NoOptionError


PATH = {'win32': lambda:
            os.path.join(os.environ['APPDATA'], 'M30W', 'M30W.conf'),
        'cygwin': lambda: 
            os.path.join(os.environ['APPDATA'], 'M30W', 'M30W.conf'),
        'linux2': lambda: os.path.expanduser('~/.config/M30W/M30W.conf'),
        'darwin': lambda:
            os.path.expanduser('~/Library/Application Support/M30W/M30W.conf')
        }[sys.platform]()

if not os.path.exists(PATH):
    try:
        if not os.path.isdir(os.path.dirname(PATH)):
            os.mkdir(os.path.dirname(PATH))
        open(PATH, 'w')
    except (OSError, IOError):
        raise SystemExit("Could not create config file at path '%s'" % PATH)

config = Parser()
config.read(PATH)

if not config.has_section('SETTINGS'):
    config.add_section('SETTINGS')


def get_option(option, default, do_eval=False):
    """get_option(option, default, do_eval=False) -> value

    Returns the value of the option specified. Returns default if
    non-existent and assigns new option to it. If eval is True it returns
    evaluated answer (e.g. tuple, int, etc.)
    """
    try:
        value = config.get('SETTINGS', option)
        return eval(value) if do_eval else value
    except NoOptionError:
        set_option(option, default)
        return default


def set_option(option, value):
    """set_option(option, value)

    Sets the option specified to the value specified.
    """
    config.set('SETTINGS', option, value)


def del_option(option):
    """del_option(option)

    Deletes the option from the file.
    """
    config.remove_option('SETTINGS', option)


def save():
    """save()

    Saves configurations to the config file.
    """
    with open(PATH, 'w') as config_file:
        config.write(config_file)

__all__ = (del_option, set_option, get_option, save)
