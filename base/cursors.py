from PyQt6.QtGui import QCursor, QPixmap
from base.folders import cursors, folder
import os

class CursorCreator:
    @staticmethod
    def create(path, x=27, y=27):
        if os.path.exists(f"{path}.png"):
            return QCursor(QPixmap(f"{path}.png"), x, y)
        else:
            folder.log.write(f"Cursor <{path}.png> not found")
            return QCursor() 

class CursorMeta(type):
    cache = {}
    
    def __getattr__(cls, name) -> QCursor:
        if name in cls.cache:
            return cls.cache[name]
        cursor = CursorCreator.create(cursors.path(name))
        cls.cache[name] = cursor
        return cursor

class Cursor(metaclass=CursorMeta):
    pass
