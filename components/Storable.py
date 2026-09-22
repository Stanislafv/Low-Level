from __future__ import annotations

from typing import TYPE_CHECKING

from base.font import Font
from base.MusicPlayer import MusicPlayer

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Storable():
    save = ("storage",)
    def __init__(self, owner:SceneObject, storage:dict|None, max_size:int):
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

        self.storage = storage
        self.max_size = max_size

    def add(self, item, count):
        if count == 0:
            return True
        if item in self.dict():
            self.storage[item] += count
        else:
            self.storage[item] = count
    
        if self.storage[item] > self.max_size: 
            self.storage[item] = self.max_size
            self.upd()
            return False
        self.upd()
        return True
    
    def empty(self):
        if len(self.dict()) == 0:
            return True
        return False
        
    def reduce(self, item, count):
        if item in self.dict():
            self.dict()[item] -= count
        else:
            self.upd()
            return False
            
        if self.dict()[item] < 0: 
            del self.dict()[item]
            self.upd()
            return False
        self.upd()
        return True
    
    def dict(self) -> dict:
        return self.storage
    
    def show(self):
        if len(self.dict()) == 0:
            return "Empty"
            
        ex = ""
    
        for name, value in self.dict().items():
            ex += f"{name}: {value}\n"
    
        return ex[:-1]
        
    def __eq__(self, f:Storable):
        return self.dict() == f.dict()
    
    def __len__(self):
        return len(self.dict())

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