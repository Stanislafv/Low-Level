from __future__ import annotations
from typing import Callable

from composites.Block import Block

from components.Updatable import Updatable
from components.Storable import Storable
from components.Clickable import Clickable
from components.Removable import Removable
from components.Switchable import Switchable
from components.Temperaturable import Temperaturable

import random

from base.folders import block_config

from ui.Widgets import AutoUI

def generate_ore_upd(name) -> Callable:
    def func(obj:Drill, task):
        if obj.components[Switchable].state is False:
            return

        task.ms /= max(obj.components[Temperaturable].coef, 0.05)

        if obj.components[Storable].add(name, 1):   
            obj.components[Temperaturable].value += 25

    return func

class Drill(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_size = block_config[self.name].get("max_storage", 10)

        self.components[Storable] = Storable(self, None, max_size)
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())
        self.components[Removable] = Removable(self, Storable.remove)
        self.components[Switchable] = Switchable(self, False)
        self.components[Temperaturable] = Temperaturable(self, -30, 140, 220)

        self.components[Updatable] = Updatable(self, [])

        self.ores:list[str] = []
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
                    self.ores.append(block.name)

        for ore in self.ores:
            resource = block_config[ore]["mining_type"]
            speed = block_config[ore]["mining_speed"]

            task = self.components[Updatable].every(speed, generate_ore_upd(resource))
            task.progress = random.uniform(0, speed)
