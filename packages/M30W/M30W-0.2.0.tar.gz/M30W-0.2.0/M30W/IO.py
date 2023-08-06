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

"""
Provides IO functions
"""
import M30W.runtime as runtime
from M30W.debug import debug
from M30W.project import Project

def save():
    runtime.project.save()

def save_as(path):
    old_path = runtime.project.path
    try:
        runtime.project.path = path
        save()
    except Exception:
        runtime.project.path = old_path
        raise

def open(path):
    old_path = runtime.project.path
    try:
        runtime.project.path = path
        reload()
    except Exception:
        runtime.project.path = old_path
        raise

def reload():
    #Referencing to old sprites, so panels won't be garbage-collected
    refs = [runtime.project.stage] + runtime.project.sprites
    runtime.project.load()
    runtime.project.changed = False
    refresh()

def new():
    runtime.project = Project()
    refresh()

def refresh():
    debug("Updating SpritePanel...", 1)
    runtime.spritePanel.UpdateList()
    debug("Done.", -1)
    debug("Refreshing stage...", 1)
    runtime.stage.Refresh()
    debug("Done.", -1)
    debug("Refreshing the notebook...", 1)
    runtime.leftPanel.RefreshPages()
    debug("Done.", -1)