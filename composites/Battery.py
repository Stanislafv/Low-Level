from __future__ import annotations

from composites.Block import Block

from base.folders import block_config
from base.functions import get_texture

from components.Powerable import Powerable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable

class Battery(Block):
    def __init__(self, *args, **kwargs):
        self.stored = 0
        super().__init__(*args, **kwargs)
        self.max_stored = block_config[self.name].get("max_stored_energy", 10)

        self.components[Powerable] = Powerable(self, 0.1)
        self.components[Updatable] = Updatable(self, [(1000, Powerable.update), (10, self.update)])
        self.components[Removable] = Removable(self, Powerable.remove)
        self.components[Placable] = Placable(self, Powerable.place)

        if self.w.scene is not None:
            self.center = self.w.scene.addPixmap(get_texture("core_1"))
            self.center.setPos((self.x+self.size[0]/2)*32-8, (self.y+self.size[1]/2)*32-8)
            self.center.setZValue(40)
            self.center.setOpacity(0)

    @staticmethod
    def update(obj:Battery):
        obj.center.setOpacity(obj.stored/obj.max_stored)
        if obj.components[Powerable].energy > 0.08:
            excess = obj.components[Powerable].energy - 0.05
            charge = min(excess, obj.max_stored - obj.stored)
            obj.stored += charge
            obj.components[Powerable].energy -= charge
        
        elif obj.components[Powerable].energy < 0.05 and obj.stored > 0:
            discharge = min(0.1 - obj.energy, obj.stored, 0.5)
            obj.components[Powerable].energy += discharge
            obj.stored -= discharge
