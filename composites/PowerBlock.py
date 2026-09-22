from base.folders import block_config

from composites.Block import Block

from components.Powerable import Powerable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable

class PowerBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        max_energy = block_config[self.name].get("max_energy", 0.1)

        self.components[Powerable] = Powerable(self, max_energy)
        self.components[Updatable] = Updatable(self, [(1000, Powerable.update)])
        self.components[Removable] = Removable(self, Powerable.remove)
        self.components[Placable] = Placable(self, Powerable.place)