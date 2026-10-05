from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6.QtCore import Qt

from base.font import Font
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor
from base.folders import folder

from ui.Menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from composites.Block import Block

class Widgets:
    pass

class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Cursor.Hand)

class Labels:
    def __new__(cls, *args, role=None, centered=False, **kwargs) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(*args, **kwargs)
        if role is not None:
            label.setProperty("role", role)
        if centered:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(Font.Bold) 
        return label

    @staticmethod
    def Title(*args, centered=False, **kwargs) -> QtWidgets.QLabel:
        return Labels(role="title", centered=centered, *args, **kwargs)

    @staticmethod
    def Subtitle(*args, centered=False, **kwargs) -> QtWidgets.QLabel:
        return Labels(role="subtitle", centered=centered, *args, **kwargs)

    @staticmethod
    def Body(*args, **kwargs) -> QtWidgets.QLabel:
        return Labels(role="body", *args, **kwargs)

    @staticmethod
    def Dim(*args, **kwargs) -> QtWidgets.QLabel: 
        return Labels(role="dim", *args, **kwargs)

    @staticmethod
    def Accent(*args, **kwargs) -> QtWidgets.QLabel:
        return Labels(role="accent", *args, **kwargs)

    @staticmethod
    def Danger(*args, **kwargs) -> QtWidgets.QLabel:
        return Labels(role="danger", *args, **kwargs)

    @staticmethod
    def Mono(*args, **kwargs) -> QtWidgets.QLabel:
        return Labels(role="mono", *args, **kwargs)

class Buttons:
    def __new__(cls, *args, role=None, **kwargs) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(*args, **kwargs)
        if role is not None:
            btn.setProperty("role", role)
        btn.setFont(Font.Bold)
        btn.setCursor(Cursor.Hand)
        btn.clicked.connect(lambda a: MusicPlayer.play("click_1")) 
        return btn

    @staticmethod
    def Primary(*args, **kwargs) -> QtWidgets.QPushButton:
        return Buttons(role="primary", *args, **kwargs)
    
    @staticmethod
    def Secondary(*args, **kwargs) -> QtWidgets.QPushButton:
        return Buttons(role="secondary", *args, **kwargs)
    
    @staticmethod
    def Danger(*args, **kwargs) -> QtWidgets.QPushButton:
        return Buttons(role="danger", *args, **kwargs)
    
    @staticmethod
    def Toggle(*args, **kwargs) -> QtWidgets.QCheckBox:
        btn = QtWidgets.QCheckBox(*args, **kwargs)
        btn.setFont(Font.Bold)
        btn.setCursor(Cursor.Hand)
        btn.clicked.connect(lambda a: MusicPlayer.play("click_1"))
        return btn

    @staticmethod
    def Icon(*args, **kwargs) -> QtWidgets.QToolButton:
        btn=QtWidgets.QToolButton(*args, **kwargs)
        btn.setFont(Font.Bold)
        btn.setCursor(Cursor.Hand)
        btn.clicked.connect(lambda a: MusicPlayer.play("click_1"))
        return btn

class Sliders:
    def __new__(cls, *args, role:str=None, **kwargs) -> QtWidgets.QSlider:
        s = QtWidgets.QSlider(*args, **kwargs)
        s.setCursor(Cursor.Hand)
        if role is not None:
            s.setProperty("role", role)
        return s

    @staticmethod
    def Horizontal(*args, **kwargs) -> QtWidgets.QSlider:
        return Sliders(QtCore.Qt.Orientation.Horizontal, role="horizontal", *args, **kwargs)

    @staticmethod
    def Vertical(*args, **kwargs) -> QtWidgets.QSlider:
        return Sliders(QtCore.Qt.Orientation.Vertical, role="vertical", *args, **kwargs)

class AutoUI(Menu):
    def __init__(self, block:Block, *args, **kwargs):
        super().__init__(block.w.window, *args, **kwargs)
        MusicPlayer.play("click_1")

        self.widgets:list[AutoUI.Component] = []

        layout = QtWidgets.QVBoxLayout(self)
                
        title = Labels.Title("Information")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(5)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.content)

        layout.addWidget(self.scroll)

        for value in block.components.values():
            if hasattr(value, "ui"):
                w = value.ui()
                self.widgets.append(w)
                self.content_layout.addWidget(w)

        layout.addStretch()
        
        btn_back = Buttons.Secondary("Back")
        
        btn_back.clicked.connect(lambda: self.Back())
        
        layout.addWidget(btn_back)
        
        self.setFixedSize(600, 800)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100)

        self.Back()

    def refresh(self):
        for widget in self.widgets:
            widget.refresh()

    def Back(self, *args):
        super().Back(*args)
        self.timer.stop()

    def Show(self, *args):
        super().Show(*args)
        self.timer.start()

    class Component(QtWidgets.QFrame):
        def __init__(self, obj):
            super().__init__(obj.owner.w.window)
            self.setProperty("role", "AutoUIComponent") 
            self.obj = obj

        def refresh(self):
            folder.log.write(f"Component <{self.__class__.__name__}> lacks a refresh method", type="AutoUIError", set_error=True)

        def __repr__(self):
            return "AutoUIComponent"
