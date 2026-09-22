from __future__ import annotations

from composites.Block import Block

from components.Storable import Storable
from components.Updatable import Updatable

from base.folders import block_config

class Conveyor(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.direction_start = block_config[self.name]["direction_start"]
        self.direction_end = block_config[self.name]["direction_end"]

        self.components[Storable] = Storable(self, None, 1)
        self.components[Updatable] = Updatable(self, [(1000, self.upd)])

    @staticmethod
    def upd(obj:Conveyor):    
        start_block:list[Block] = obj.w.block_map.get((obj.x - obj.direction_start[0], obj.y - obj.direction_start[1]))
        end_block:list[Block] = obj.w.block_map.get((obj.x - obj.direction_end[0], obj.y - obj.direction_end[1]))

        if start_block is not None:
            for block in start_block:
                if Storable in block.components:
                    if not block.components[Storable].empty():
                        for item in block.components[Storable].dict():
                            if obj.components[Storable].add(item, 1):
                                block.components[Storable].reduce(item, 1)
                                break

        if end_block is not None:
            for block in end_block:
                if Storable in block.components:
                    if hasattr(block, "direction_start"):
                        if obj.direction_start == block.direction_start and obj.direction_end == block.direction_end:
                            return
                        
                    if not obj.components[Storable].empty():
                        for item in obj.components[Storable].dict():
                            if block.components[Storable].add(item, 1):
                                obj.components[Storable].reduce(item, 1)
                                break
