from __future__ import annotations

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from components.Storable import Storable

from base.functions import save
from base.font import Font
from base.cursors import Cursor
from base.MusicPlayer import MusicPlayer
from base.folders import folder, mainfolder

branchs:dict = mainfolder.read("branch_config.json", type="json")

from ui.Menu import Menu

class TechTreeMenu(Menu):
    @save
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        title = QLabel("Tree")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(Font.Bold)
        title.setStyleSheet("font-size: 20px")

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(5)

        coef = folder.config["craft_coef"]

        if not folder.config.get("devmode", False):
            for name, value in branchs.items():
                text = "\n".join(f"{item.capitalize()}: {int(count*coef)}" for item, count in value["cost"].items())
                btn = QtWidgets.QPushButton(f"{name}\n{text}")
                btn.setFont(Font.Bold)
                btn.setCursor(Cursor.Hand)
                btn.clicked.connect(lambda i, btn=btn, v=value: self.open(v["open"], v["cost"], btn))
                btn.setStyleSheet("font-size: 20px")
                btn.setFixedHeight(150)
                
                layout.addWidget(btn)

        else:
            label = QtWidgets.QLabel("DEV MODE ON")
            label.setFont(Font.Bold)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

        layout.addStretch()

        btn_back = QtWidgets.QPushButton("Back")
        btn_back.setFont(Font.Bold)
        btn_back.setCursor(Cursor.Hand)
        btn_back.clicked.connect(lambda: self.Back())
        btn_back.clicked.connect(lambda: MusicPlayer.play("click_1"))

        layout.addWidget(btn_back)
        
        self.setFixedSize(QtCore.QSize(self.parent().width(), self.parent().height()))

        self.setFixedSize(600, 800)

    @save
    def open(self, names:list, cost:dict, btn:QtWidgets.QPushButton=None):
        MusicPlayer.play("click_1")
        coef = folder.config["craft_coef"]

        for name, value in cost.items():
            v = self.Window.manager.current.Base.components[Storable].dict().get(name, 0)
            if v < value:
                MusicPlayer.play("error_1")
                return

        for name, value in cost.copy().items():
            self.Window.manager.current.Base.components[Storable].reduce(name, int(value*coef))
            
        for name in names:
            if name not in self.Window.manager.current.opened:
                self.Window.manager.current.opened.append(name)

        btn.setEnabled(False)

        self.Window.update_tool_panel()