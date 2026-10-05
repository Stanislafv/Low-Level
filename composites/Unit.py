from __future__ import annotations

import applib
from base.folders import folder
from base.MusicPlayer import MusicPlayer
from base.functions import safe_class, get_texture
from base.folders import unit_config
from components.SceneObject import SceneObject

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.World import World

@safe_class
class Unit(SceneObject):
    save = ("x", "y", "name")
    def __init__(self, w:World, x:float, y:float, name:str):
        super().__init__(w, x, y, name)
 
        self._x:float = x
        self._y:float = y

        self.place()

    def draw(self):
        if self.w.scene is not None:
            self.pixmap = get_texture(self.name)
            self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
            self.pixmap_item.setTransformOriginPoint(self.pixmap.width() / 2, self.pixmap.height()  / 2)
            self.pixmap_item.setPos(self.x, self.y)
            self.pixmap_item.setZValue(40)
        else:
            print("нет сцены")

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value:float):
        self._x = value
        if hasattr(self, "pixmap_item"):
            self.pixmap_item.setX(value)

    @property
    def y(self) -> float:
        return self._y
    
    @y.setter
    def y(self, value:float):
        self._y = value
        if hasattr(self, "pixmap_item"):
            self.pixmap_item.setY(value)

    def place(self):
        if hasattr(self, "pixmap_item"):
            folder.log.write("2 раза ставишь", type=applib.ERROR)
            return False
                
        self.draw()
        self.w.append_unit(self)
        if self.w.scene is not None:
            self.w.scene.update()
        return True

    def get_occupied_cells(self):
        cells = set()
        width_tiles = self.pixmap_item.pixmap().width() // 32
        height_tiles = self.pixmap_item.pixmap().height() // 32
        
        for dx in range(width_tiles):
            for dy in range(height_tiles):
                cells.add((int(self.x) + dx, int(self.y) + dy))
        return cells

    def remove(self):

        if not self.exists:
            return
        self.exists = False
        if hasattr(self, 'pixmap_item'):
            self.w.scene.removeItem(self.pixmap_item)
            self.w.scene.update()
        if self in self.w.entities:
            self.w.entities.remove(self)

    def __repr__(self):
        output = ""
        for name, value in self.__dict__.items():
            output += f"{name}: {value}, "
        return f"<{type(self).__name__}({output[:-2]})>"