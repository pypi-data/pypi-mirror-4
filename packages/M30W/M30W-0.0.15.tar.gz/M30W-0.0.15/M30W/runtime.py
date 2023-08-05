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

#Other modules should use the provided methods to change sprites.
def get_sprites():
    return tuple(project.sprites)

def get_stage():
    return project.stage

def add(sprite):
    if sprite.name in map(lambda x: x.name, project.sprites):
        raise NameError("Sprite %s already registered!" % sprite.name)
    project.sprites.append(sprite)
    spritePanel.UpdateList(len(project.sprites))


def new():
    names = map(lambda x: x.name, project.sprites)
    for i in xrange(1000):
        if 'new_sprite %s' % i in names: continue
        add(Sprite('new_sprite %s' % i))
        return project.sprites[-1]

def delete(index):
    project.sprites.pop(index)
    spritePanel.UpdateList(0)

def delete_all():
    del project.sprites[:]
    spritePanel.RecreateList(0)

def replace_all(new_sprites):
    project.sprites[:] = new_sprites
    spritePanel.RecreateList(0)

def moveup(index):
    if not index > 0:
        return
    (project.sprites[index],
     project.sprites[index - 1]) = (project.sprites[index - 1],
                                    project.sprites[index])
    spritePanel.UpdateList(index)

def movedown(index):
    if not index < len(project.sprites):
        return
    (project.sprites[index],
     project.sprites[index + 1]) = (project.sprites[index + 1],
                                    project.sprites[index])
    spritePanel.UpdateList(index + 2)
