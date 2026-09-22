from __future__ import annotations
from composites.Block import Block
from base.folders import block_config

from components.Storable import Storable
from components.Powerable import Powerable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable
from components.Clickable import Clickable

class Generator(Block):
    def __init__(self, *args, **kwargs):
        self.mining_progress = 0
        super().__init__(*args, **kwargs)

        max_storage = block_config[self.name].get("max_storage", 10)
        mining_speed = block_config[self.name].get("mining_speed", 1)
        max_energy = block_config[self.name].get("max_energy", 1)

        self.mining_type = block_config[self.name].get("mining_type", "coal")
        self.energy_add = block_config[self.name].get("energy_add", 1)

        self.components[Storable] = Storable(self, None, max_storage)
        self.components[Powerable] = Powerable(self, max_energy)
        self.components[Updatable] = Updatable(self, [(mining_speed, self.upd), (1000, Powerable.update)])
        self.components[Removable] = Removable(self, lambda obj: [Powerable.remove(obj), Storable.remove(obj)])
        self.components[Placable] = Placable(self, Powerable.place)
        self.components[Clickable] = Clickable(self, Storable.click)

    @staticmethod
    def upd(obj:Generator):
        if obj.mining_type in obj.components[Storable].dict(): 
            obj.components[Storable].reduce(obj.mining_type, 1)
            obj.components[Powerable].energy = min(obj.components[Powerable].energy+obj.energy_add, obj.components[Powerable].max_energy)
