from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget

from ui.Widgets import Labels, Buttons

from base.functions import get_texture, safe_class
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor
from base.folders import folder, saves

from ui.GameWindow import GameWindow
from ui.EditorWindow import EditorWindow

@safe_class
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

    def update_layout(self, window:GameWindow):
        title = Labels.Title("Choice sector")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout:QtWidgets.QVBoxLayout = self.layout()

        SectorChoiceWindow.clear_layout(layout)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(5)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)

        layout.addWidget(self.scroll)

        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        
        self.scroll.setWidget(self.content)
        
        for save_name in saves.list():
            save = saves.mkdir(save_name)
            btn = Buttons.Icon()
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setProperty("role", "secondary")
            btn.setText(save_name.replace("_", " ".title())) 
            btn.setIcon(QIcon(QPixmap(save.path("ViewMap.png"))))
            btn.setIconSize(QSize(256, 256))
    
            btn.clicked.connect(lambda a=None, w=window, name=save_name: [w.manager.switch_to(name), w.show()])
        
            self.content_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(10)
        
        btn_back = Buttons.Secondary("Back")
        layout.addWidget(btn_back)
        btn_back.clicked.connect(lambda: self.MainWindow.MenuWindow.show())
        
        layout.addStretch()

    def show(self, window:GameWindow):
        if len(saves.list()) == 0:
            window.show()
            return

        self.MainWindow.widget.setCurrentIndex(3)
        self.update_layout(window)

@safe_class
class MenuWindow(QWidget):
    def __init__(self, window:MainWindow):
        super().__init__(window)

        self.MainWindow = window

        self.setCursor(Cursor.Cursor)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        left_panel = QtWidgets.QVBoxLayout()
        left_panel.setSpacing(10)

        left_panel.addStretch()
        
        title = Labels.Title("LOW-LEVEL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(title)
        
        btn_sandbox = Buttons.Primary("Sandbox")
        btn_settings = Buttons.Secondary("Settings")
        btn_exit = Buttons.Secondary("Exit")
        btn_editor = Buttons.Secondary("Editor")
        
        for btn in [btn_sandbox, btn_settings, btn_editor, btn_exit]:
            btn.setFixedSize(300, 80)
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
        
        btn_sandbox.clicked.connect(lambda: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.GameWindow))
        btn_settings.clicked.connect(lambda: ...)
        btn_editor.clicked.connect(lambda: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.EditorWindow))

        btn_exit.clicked.connect(self.MainWindow.close)

    def play(self):
        MusicPlayer.play("click_2")
        self.MainWindow.GameWindow.show()

    def show(self):
        self.MainWindow.widget.setCurrentIndex(0)

@safe_class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Low-Level")
        self.setWindowIcon(QIcon(get_texture("icon")))
        self.setCursor(Cursor.Cursor)

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