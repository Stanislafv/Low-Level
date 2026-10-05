from __future__ import annotations

from ui.Widgets import Labels, Buttons, AutoUI
from ui.Menu import Menu
from PyQt6 import QtWidgets

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Switchable:
    save = ("state",)
    def __init__(self, owner:SceneObject, state:bool, func:Callable|None=None):
        self.owner = owner
        self.state:bool = state
        self.func = func

    def ui(self):
        class w(AutoUI.Component):
            def __init__(self, obj:Switchable):
                super().__init__(obj)
                
                layout = QtWidgets.QVBoxLayout(self)  
                self.btn = Buttons.Toggle("Working")
                self.btn.setChecked(self.obj.state)
                if self.obj.func is not None:
                    self.btn.clicked.connect(lambda: self.obj.func(self.obj))

                layout.addWidget(self.btn)
        
            def refresh(self):
                self.obj.state = bool(self.btn.checkState().value)

        return w(self)