from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from ui.SettingsMenu import SettingsMenu
from ui.TechTreeMenu import TechTreeMenu

from ui.Widgets import Labels, Buttons

from ui.Menu import Menu

class PauseMenu(Menu):
    def __init__(self, *args, **k):
        super().__init__(*args, **k)

        layout = QtWidgets.QVBoxLayout(self)
                
        label = Labels.Title("Pause")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
        btn_resume = Buttons.Secondary("Resume")
        btn_resume.clicked.connect(self.Back)  
                
        btn_exit = Buttons.Secondary("Exit")
        btn_exit.clicked.connect(lambda: self.Window.close()) 

        btn_tree = Buttons.Secondary("Techonology Tree")
        btn_tree.clicked.connect(lambda: self.show_window_tree())

        btn_settings = Buttons.Secondary("Settings")
        btn_settings.clicked.connect(lambda: self.settings.Show())

        layout.addWidget(label)

        for btn in [btn_resume, btn_exit, btn_tree, btn_settings] if not self.Window.manager.current.devmode else [btn_resume, btn_exit, btn_settings]:
            layout.addWidget(btn)
                
        self.setFixedSize(250, 200)

        self.settings = SettingsMenu(self.Window, self)

        if not self.Window.manager.current.devmode:
            self.tree = TechTreeMenu(self.Window, None)
        else:
            self.tree = None

    def show_window_tree(self): 
        self.tree.Parent = self
        self.tree.Show()

