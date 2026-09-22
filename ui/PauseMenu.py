from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from base.functions import save
from base.font import Font
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor

from ui.SettingsMenu import SettingsMenu
from ui.TechTreeMenu import TechTreeMenu
from ui.Menu import Menu

class PauseMenu(Menu):
    @save
    def __init__(self, *args, **k):
        super().__init__(*args, **k)

        layout = QtWidgets.QVBoxLayout(self)
                
        label = QLabel("Pause")
        label.setFont(Font.Bold)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
        btn_resume = QtWidgets.QPushButton("Resume")
        btn_resume.clicked.connect(self.Back)  
                
        btn_exit = QtWidgets.QPushButton("Exit")
        btn_exit.clicked.connect(lambda: self.Window.close()) 

        btn_tree = QtWidgets.QPushButton("Techonology Tree")
        btn_tree.clicked.connect(lambda: self.show_window_tree())

        btn_settings = QtWidgets.QPushButton("Settings")
        btn_settings.clicked.connect(lambda: self.settings.Show())

        layout.addWidget(label)

        for btn in [btn_resume, btn_exit, btn_tree, btn_settings] if not self.Window.manager.current.devmode else [btn_resume, btn_exit, btn_settings]:
            btn.setFont(Font.Bold)
            btn.setCursor(Cursor.Hand)
            btn.clicked.connect(lambda: MusicPlayer.play("click_1")) 
            layout.addWidget(btn)
                
        self.setFixedSize(200, 150)

        self.settings = SettingsMenu(self.Window, self)

        if not self.Window.manager.current.devmode:
            self.tree = TechTreeMenu(self.Window, None)
        else:
            self.tree = None

    @save
    def show_window_tree(self): 
        self.tree.Parent = self
        self.tree.Show()

