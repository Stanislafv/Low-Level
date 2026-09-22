from __future__ import annotations

from base.folders import folder, block_config
import applib
import base.functions as func
from base.MusicPlayer import MusicPlayer
from PyQt6.QtWidgets import QGraphicsItem

from components.SceneObject import SceneObject

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.World import World

class Block(SceneObject):
    @func.save
    def __init__(self, w:World, x:int, y:int, name:str, team:str, **kwargs):
        if x >= w.sizeX or y >= w.sizeY or x < 0 or y < 0:
            self.exists = False
            folder.log.write(f"Block <{name}(x:{x}, y:{y})> Located behind the world", type="BlockData")

        super().__init__(w, x, y, name, team)
        
        self.pixmap = func.get_texture(self.name)
        self.size = (self.pixmap.width()//32, self.pixmap.height()//32)

        self.temperature = self.w.temperature

        for name, value in kwargs.items():
            self.__setattr__(name, value)

        self.place()
    
    def draw(self):
        if self.exists and self.w.scene is not None:
            self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
            if block_config[self.name].get("centered", False):
                self.pixmap_item.setPos((self.x-(self.size[0]/4))*32, (self.y-(self.size[1]/4))*32)
            else:
                self.pixmap_item.setPos(self.x*32, self.y*32)
            self.pixmap_item.setZValue(block_config[self.name]["z"])  
            self.pixmap_item.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def get_occupied_cells(self) -> set[tuple[int | float, int | float]] | set:
        if block_config[self.name].get("centered", False):
            return {(self.x, self.y)}
        cells = set()
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                cells.add((self.x + dx, self.y + dy))
        return cells

    def get_around(self):
        cells = set()
        for cell in self.get_occupied_cells():
            for coef in ((1, 0), (-1, 0), (0, 1), (0,-1)):
                cells.add((cell[0]+coef[0], cell[1]+coef[1]))
        return cells 

    @func.save
    def place(self):
        if hasattr(self, "pixmap_item"):
            folder.log.write("2 раза ставишь", type=applib.ERROR)
            return False
        
        for cell in self.get_occupied_cells():
            blocks = self.w.block_map.get(cell)
            if blocks is None:
                continue
            for block in blocks:
                if block is self or block_config[block.name]["z"] < 20:
                    continue
                return False
            
        self.draw()
        MusicPlayer.play("place", volume=0.7)
        self.w.append_block(self)
        if self.w.scene is not None:
            self.w.scene.update()
        return True

    def info(self):
            output = ""
            for name, value in self.__dict__.items():
                output += f"{name}: {value}, "
            return f"<{type(self).__name__}({output[:-2]})>"

    def upd(self):
        if block_config[self.name].get("relief", False):
            return

        for coords in self.get_around():
            block:Block = self.w.get_block_at(*coords)
            if block is None:
                if self.temperature > self.w.temperature:
                    self.temperature -= 0.02
                continue

            if abs(self.temperature - block.temperature) < 0.1:
                continue

            delta = (self.temperature - block.temperature)*0.1
            block.temperature += delta
            self.temperature -= delta

    def __repr__(self):
        return f"TEMPERATURE: {self.temperature}, <{type(self).__name__}>"