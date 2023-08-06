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

"""Module to store objects at runtime.
Objects are either set to None if not yet created.
GUI parts are:
* mainFrame
* leftPanel
* rightPanel
* noteBook (the coding area)
* stage
* spritePanel
Non-GUI objects are:
* sprites
"""
mainFrame = leftPanel = rightPanel = noteBook = stage = spritePanel = None

#global project, sprites, Sprite, stage
from M30W.project import Project
from M30W.sprites import Sprite
project = Project()
project.changed = False

#Other modules should use the provided methods to change sprites.
def get_sprites():
    return project.sprites

def get_stage():
    return project.stage

def add(sprite):
    if sprite.name in map(lambda x: x.name, project.sprites):
        raise NameError("Sprite %s already registered!" % sprite.name)
    project.sprites.append(sprite)

def new():
    names = map(lambda x: x.name, project.sprites)
    for i in xrange(1000):
        if 'Sprite %s' % i in names: continue
        add(Sprite('Sprite %s' % i))
        return project.sprites[-1]

def delete(index):
    project.sprites.pop(index)
