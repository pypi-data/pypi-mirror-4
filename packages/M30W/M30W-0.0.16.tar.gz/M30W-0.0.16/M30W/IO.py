"""
Provides IO functions
"""
import M30W.runtime as runtime
from M30W.debug import debug

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
    debug("Updating SpritePanel...", 1)
    runtime.spritePanel.UpdateList()
    debug("Done.", -1)
    debug("Refreshing stage...", 1)
    runtime.stage.Refresh()
    debug("Done.", -1)
    debug("Refreshing the notebook...", 1)
    runtime.leftPanel.RefreshPages()
    debug("Done.", -1)
