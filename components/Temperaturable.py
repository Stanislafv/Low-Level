from __future__ import annotations

from ui.Widgets import Labels, AutoUI
from PyQt6 import QtWidgets

from typing import TYPE_CHECKING
import math
if TYPE_CHECKING:
    from components.SceneObject import SceneObject

def efficiency(x, x_min, x_opt, x_max) -> float:
    if x <= x_opt:
        t = (x - x_min) / (x_opt - x_min)  
    else:
        t = (x_max - x) / (x_max - x_opt)  
    t = max(0.0, min(1.0, t))            
    return math.sin(t * math.pi / 2)

class Temperaturable:
    def __init__(self, owner:SceneObject, min:int, opt:int, max:int):
        self.owner = owner
        self.min = min
        self.opt = opt
        self.max = max

    @property
    def value(self):
        return self.owner.w.temperature.field[self.owner.y, self.owner.x]

    @value.setter
    def value(self, value):
        for i in self.owner.get_occupied_cells():
            self.owner.w.temperature.field[i[1], i[0]] = value

    @property
    def coef(self):
        return efficiency(self.value, self.min, self.opt, self.max)

    def ui(self):
        class w(AutoUI.Component):
            def __init__(self, obj:Temperaturable):
                super().__init__(obj)
                        
                layout = QtWidgets.QVBoxLayout(self)  

                self.label = Labels.Body(f"Temperature: {self.obj.value:.2f}℃")

                layout.addWidget(self.label)
        
            def refresh(self):
                self.label.setText(f"Temperature: {self.obj.value:.2f}℃")
        
        return w(self)