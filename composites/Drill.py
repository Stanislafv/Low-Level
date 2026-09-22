from __future__ import annotations

from composites.Block import Block

from components.Updatable import Updatable
from components.Storable import Storable
from components.Clickable import Clickable
from components.Removable import Removable

from base.folders import block_config

class Drill(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mining_speed = block_config[self.name].get("mining_speed", 1000)
        max_size = block_config[self.name].get("max_storage", 10)

        self.components[Storable] = Storable(self, None, max_size)
        self.components[Updatable] = Updatable(self, [(mining_speed, self.upd)])
        self.components[Clickable] = Clickable(self, Storable.click)
        self.components[Removable] = Removable(self, Storable.remove)

        self.ores = []
        for cell in self.get_occupied_cells():
            blocks = self.w.block_map.get(cell)
            if blocks is None:
                continue
            for block in blocks:
                if block is None or block is self:
                    continue
                if block_config[block.name]["z"] not in (14, 15):
                    continue
                if block_config[block.name]["mining_type"] is not None:
                    self.ores.append(block_config[block.name]["mining_type"])

    @staticmethod
    def upd(obj:Drill):
        for ore in obj.ores:
            obj.components[Storable].add(ore, 1)
