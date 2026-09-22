from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget

import sys, applib

from ui.EditorWindow import SectorManager

from base.functions import save, get_texture
from base.font import Font
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor
from base.folders import folder, saves

from ui.GameWindow import GameWindow
from ui.EditorWindow import EditorWindow

class SectorChoiceWindow(QWidget):
    def __init__(self, window:MainWindow):
        super().__init__(window)

        self.MainWindow = window
        self.setCursor(Cursor.Cursor)

        layout = QtWidgets.QVBoxLayout(self)

        self.hide()

    @staticmethod
    def clear_layout(layout:QtWidgets.QVBoxLayout):
        if layout is None:
            return
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    SectorChoiceWindow.clear_layout(child_layout)

    def update_layout(self, window:GameWindow, editor=False):
        title = QtWidgets.QLabel("Choice sector")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(Font.Bold)
        title.setStyleSheet("font-size: 20px")

        layout:QtWidgets.QVBoxLayout = self.layout()

        SectorChoiceWindow.clear_layout(layout)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(5)
        
        for save_name in saves.list():
            save = saves.mkdir(save_name)
            btn = QtWidgets.QPushButton(save_name.replace("_", " ".title()))
            btn.setFont(Font.Bold)
            btn.setCursor(Cursor.Hand)
            btn.setIcon(QIcon(QPixmap(save.path("ViewMap.png"))))
            btn.setIconSize(QSize(256, 256))
        
            btn.clicked.connect(lambda a=None, w=window, name=save_name: [self.MainWindow.GameWindow.manager.switch_to(name), w.show()] if not editor else [self.MainWindow.GameWindow.manager.switch_to(name), w.show()])
        
            layout.addWidget(btn)
        
        layout.addSpacing(5)
        
        btn_new = QtWidgets.QPushButton("Empty")
        btn_back = QtWidgets.QPushButton("Back")
        
        for btn in [btn_new, btn_back]:
            btn.setFont(Font.Bold)
            btn.setCursor(Cursor.Hand)
            btn.clicked.connect(lambda: MusicPlayer.play("click_1"))
            layout.addWidget(btn)
        
        btn_back.clicked.connect(lambda: self.MainWindow.MenuWindow.show())
        btn_new.clicked.connect(lambda: [window.show(), SectorManager.clear(window.world)])
        
        layout.addStretch()

    @save
    def show(self, window:GameWindow, editor=False):
        if len(saves.list()) == 0:
            window.show()
            return

        self.MainWindow.widget.setCurrentIndex(3)
        self.update_layout(window, editor)

class MenuWindow(QWidget):
    @save
    def __init__(self, window:MainWindow):
        super().__init__(window)

        self.MainWindow = window

        self.setCursor(Cursor.Cursor)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        left_panel = QtWidgets.QVBoxLayout()
        left_panel.setSpacing(10)

        left_panel.addStretch()
        
        title = QtWidgets.QLabel("LOW-LEVEL")
        title.setFont(Font.Bold) 
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(title)
        
        btn_play = QtWidgets.QPushButton("Play")
        btn_settings = QtWidgets.QPushButton("Settings")
        btn_editor = QtWidgets.QPushButton("Editor")
        btn_exit = QtWidgets.QPushButton("Exit")
        
        for btn in [btn_play, btn_settings, btn_exit, btn_editor]:
            btn.setFixedSize(300, 80)
            btn.setFont(Font.Bold)
            btn.setCursor(Cursor.Hand)
            left_panel.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        left_panel.addStretch()  

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(500)
        
        image_label = QtWidgets.QLabel()
        pixmap = QPixmap("bg.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio)
            image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(image_label)  
        
        btn_play.clicked.connect(lambda: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.GameWindow))
        btn_settings.clicked.connect(lambda: ...)
        btn_editor.clicked.connect(lambda: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.EditorWindow, editor=True))

        btn_exit.clicked.connect(self.MainWindow.close)

    def play(self):
        MusicPlayer.play("click_2")
        self.MainWindow.GameWindow.show()

    @save
    def show(self):
        self.MainWindow.widget.setCurrentIndex(0)

class MainWindow(QMainWindow):
    @save
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Low-Level")
        self.setWindowIcon(QIcon(get_texture("icon")))
        self.setCursor(Cursor.Cursor)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        self.widget = QStackedWidget()
        self.setCentralWidget(self.widget)

        self.GameWindow = GameWindow(self)
        self.MenuWindow = MenuWindow(self)
        self.EditorWindow = EditorWindow(self)
        self.SectorChoiceWindow = SectorChoiceWindow(self)

        self.widget.addWidget(self.MenuWindow)
        self.widget.addWidget(self.GameWindow)
        self.widget.addWidget(self.EditorWindow)
        self.widget.addWidget(self.SectorChoiceWindow)

        self.widget.setCurrentIndex(1 if folder.config.get("auto_start", False) else 0)

    def closeEvent(self, a0):
        folder.log._log_exit()
        a0.accept()