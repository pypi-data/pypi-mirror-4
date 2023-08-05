"""
Provides IO functions
"""
import M30W.runtime as runtime

def save():
    runtime.project.save()

def save_as(path):
    old_path = runtime.project.path
    try:
        runtime.project.path = path
        save()
    finally:
        runtime.project.path = old_path

def open(path):
    old_path = runtime.project.path
    try:
        runtime.project.path = path
        reload()
    finally:
        runtime.project.path = old_path

def reload():
    runtime.project.load()
    runtime.spritePanel.RecreateList()
    runtime.stage.Refresh()