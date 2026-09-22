from __future__ import annotations

from composites.Block import Block

from components.Storable import Storable
from components.Clickable import Clickable
from components.Removable import Removable

from base.folders import block_config

class StorageBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_size = block_config[self.name].get("max_storage", 10)

        self.components[Storable] = Storable(self, None, max_size)
        self.components[Clickable] = Clickable(self, Storable.click)
        self.components[Removable] = Removable(self, Storable.remove)
