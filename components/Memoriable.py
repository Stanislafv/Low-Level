from __future__ import annotations

from typing import TYPE_CHECKING

from base.font import Font
from base.MusicPlayer import MusicPlayer

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Memoriable():
    save = ("variables",)
    def __init__(self, owner:SceneObject, variables:dict|None, limit:int):
        self.owner = owner
        if storage is None:
            storage = {}

        if self.owner.w.scene is not None:
            self.center = self.owner.w.scene.addText("Empty")
            self.center.setPos((self.owner.x+self.owner.size[0]/2)*32-25, (self.owner.y+self.owner.size[1])*32)
            self.center.setZValue(40)
            self.center.setFont(Font.Bold)
            self.center.setOpacity(0)

        self.old_dict = {}

        self.variables = variables
        self.limit = limit

    
    def show(self):
        if len(self.dict()) == 0:
            return "Empty"
            
        ex = ""
    
        for name, value in self.dict().items():
            ex += f"{name}: {value}\n"
    
        return ex[:-1]

    def upd(self):
        if self.owner.w.scene is not None:
            if self.old_dict != self.dict():
                self.old_dict = self.dict().copy()
                text = self.show()
                self.center.setPlainText(text)

    @staticmethod
    def remove(block:SceneObject):
        if block.w.scene is not None:
            block.w.scene.removeItem(block.components[Storable].center)

    @staticmethod
    def click(block:SceneObject):
        if block.w.scene is not None:
            block.components[Storable].center.setOpacity(1 if block.components[Storable].center.opacity() == 0 else 0)
            MusicPlayer.play("click_1")