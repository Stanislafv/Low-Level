from __future__ import annotations

from composites.Block import Block

from base.folders import block_config
from base.functions import save, get_texture

from components.Powerable import Powerable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable

class Healer(Block):
    def __init__(self, *args, **kwargs):
        self.effects = set()
        max_energy = block_config[self.name].get("max_energy", 0.1)
        
        self.components[Powerable] = Powerable(self, max_energy)
        self.components[Updatable] = Updatable(self, [(1000, Powerable.update), (1000, self.update)])
        self.components[Removable] = Removable(self, Powerable.remove)
        self.components[Placable] = Placable(self, Powerable.place)

        super().__init__(*args, **kwargs)
        
        self.cells = []
        for x in range(-5, 6): 
            for y in range(-5, 6):
                if x*x + y*y <= 25:
                    self.cells.append((self.x+x, self.y+y))

    @staticmethod
    def update(obj:Healer): 
        if obj.components[Powerable].energy > 0.01:
            for x, y in obj.cells:
                block = obj.w.get_block_at(x, y)
                if block is not None:
                    if block.hp < block_config[block.name]["hardness"]:
                        obj = obj.w.scene.addPixmap(get_texture("core_1"))
                        obj.setPos((obj.x+obj.size[0]/2)*32-8, (obj.y+obj.size[1]/2)*32-8)
                        obj.setZValue(40)
                        obj.setOpacity(0.6)
                        obj.components[Powerable].energy -= 0.02
                        block.hp += 0.1
