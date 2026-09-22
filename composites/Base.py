from __future__ import annotations

from base.MusicPlayer import MusicPlayer
from base.folders import block_config

from composites.Block import Block

from components.Storable import Storable
from components.Clickable import Clickable
from components.Updatable import Updatable

class Base(Block):
    def __init__(self, *args, resource_panel=None, **kwargs):
        super().__init__(*args, **kwargs)
        max_size = block_config[self.name].get("max_storage", 10)

        self.components[Storable] = Storable(self, None, max_size)
        self.components[Clickable] = Clickable(self, self.click)
        self.components[Updatable] = Updatable(self, [(1000, self.upd)])

        self.panel = resource_panel

        # ДЕРЕВА НЕТУУУУ  А АААААААААААААААААААААААА

    @staticmethod
    def click(obj:Base):
        if obj.tree is not None:
            MusicPlayer.play("click_2")
            obj.tree.Parent = None
            obj.tree.Show()

    @staticmethod
    def upd(obj:Base):
        if obj.panel is not None:
            obj.panel.update(obj.components[Storable].dict())