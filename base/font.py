from __future__ import annotations

import os
from base.folders import folder, fonts
from PyQt6.QtGui import QFont, QFontDatabase

class FontCreator:
    @staticmethod
    def create(name, size):
        name = f"{name}.ttf"
        if os.path.exists(fonts.path(name)):
            font_id = QFontDatabase.addApplicationFont(fonts.path(name))
            families = QFontDatabase.applicationFontFamilies(font_id)
            return QFont(families[0], size)
        else:
            folder.log.write(f"Font <{name}> not found in <{fonts.file_path}>")
            return QFont("Arial", size, QFont.Weight.Bold, True)

class FontMeta(type):
    _cache = {}

    def __getattr__(cls, name) -> QFont:
        if name in cls._cache:
            return cls._cache[name]
        
        font = FontCreator.create(name, 12)
        cls._cache[name] = font
        return font

class Font(metaclass=FontMeta):
    pass