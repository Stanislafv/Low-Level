import os, sys
import base.folders as folders
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

application = QApplication(sys.argv)

class FontCreator:
    @staticmethod
    def create(name, size):
        name = f"{name}.ttf"
        if os.path.exists(folders.fonts.path(name)):
            font_id = QFontDatabase.addApplicationFont(folders.fonts.path(name))
            families = QFontDatabase.applicationFontFamilies(font_id)
            return QFont(families[0], size)
        else:
            folders.folder.log.write(f"Font <{name}> not found in <{folders.fonts.file_path}>")
            return QFont("Arial", size, QFont.Weight.Bold, True)

class Font:
    Bold:QFont = FontCreator.create("Quantico-Bold", 12)
    Bold.setBold(True)

    Regular:QFont = FontCreator.create("Quantico-Regular", 12)
    Italic:QFont = FontCreator.create("Quantico-Italic", 12)