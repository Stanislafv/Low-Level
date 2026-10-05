from __future__ import annotations

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QScrollArea

from components.Storable import Storable

from ui.Widgets import Labels, Buttons

from base.MusicPlayer import MusicPlayer
from base.functions import safe_class
from base.folders import folder, mainfolder

branchs:dict = mainfolder.read("branch_config.json", type="json")

from ui.Menu import Menu

@safe_class
class TechTreeMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)

        self.update()
        self.setFixedSize(600, 800)

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
                        TechTreeMenu.clear_layout(child_layout)
    
    def update(self):
        layout = self.layout()
        TechTreeMenu.clear_layout(layout)
                
        title = Labels.Title("Tree")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(5)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        layout.addWidget(self.scroll)
        
        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.content)
        
        coef = folder.config["craft_coef"]
        
        for name, value in branchs.items():
            text = "\n".join(f"{item.capitalize()}: {int(count*coef)}" for item, count in value["cost"].items())
            btn = Buttons.Secondary(f"{name}\n{text}")
            btn.clicked.connect(lambda i, btn=btn, v=value: self.open(v["open"], v["cost"], btn))
            btn.setFixedHeight(150)
                        
            self.content_layout.addWidget(btn)
        
        layout.addStretch()
        
        btn_back = Buttons.Secondary("Back")
        
        btn_back.clicked.connect(lambda: self.Back())
        
        layout.addWidget(btn_back)

    def open(self, names:list, cost:dict, btn:QtWidgets.QPushButton=None):
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