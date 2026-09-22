from __future__ import annotations

from composites.Block import Block

from components.Updatable import Updatable
from components.Storable import Storable
from components.Clickable import Clickable
from components.Removable import Removable

from base.folders import block_config

class Smelter(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cfg = block_config[self.name]
        self.input_item = cfg["input_item"]
        self.output_item = cfg["output_item"]
        craft_time = cfg.get("craft_time", 60)
        max_size = cfg.get("max_storage", 10)

        self.components[Storable] = Storable(self, None, max_size)
        self.components[Updatable] = Updatable(self, [(craft_time, self.upd)])
        self.components[Clickable] = Clickable(self, Storable.click)
        self.components[Removable] = Removable(self, Storable.remove)

    @staticmethod
    def upd(obj: Smelter):
        st = obj.components[Storable]
        if st.get(obj.input_item) > 0:
            st.remove(obj.input_item, 1)
            st.add(obj.output_item, 1)