from PyQt6.QtGui import QCursor, QPixmap
from base.folders import cursors
import os

from base.font import application

class CursorCreator:
    def create(path, x=27, y=27):
        if os.path.exists(f"{path}.png"):
            return QCursor(QPixmap(f"{path}.png"), x, y)
        else:
            return QCursor()

class Cursor:
    Hand = CursorCreator.create(cursors.path("hand"))
    Cursor = CursorCreator.create(cursors.path("cursor"))
