from __future__ import annotations

from PyQt6.QtCore import QRectF

from world.WorldLoader import WorldLoader

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from PyQt6.QtWidgets import QGraphicsScene

class WorldManager:
    def __init__(self, scene:QGraphicsScene, tool_panel_update:Callable|None=None, resource_panel=None, initial:str|None=None, loader=WorldLoader):
        self.loader = loader
        self.scene = scene
        self.tool_panel_update = tool_panel_update
        self.current = None
        self.current_name = None
        self.resource_panel=resource_panel
        if initial is not None:
            self.switch_to(initial)

    def load(self, name):
        self.scene.clear()
        world = self.loader.load(name, scene=self.scene)
        if self.resource_panel is not None:
            for bl in world.blocks:
                if bl.name == "base":
                    self.current.Base = bl
                    self.current.Base.panel = self.resource_panel

        self.scene.setSceneRect(QRectF(0, 0, world.sizeX*32, world.sizeY*32))
        return world

    def save(self, name):
        if self.current is not None:
            return self.loader.save(self.current, name)

    def switch_to(self, name):
        if self.current is not None:
            self.save(self.current_name)

        self.current = self.load(name)
        self.current_name = name
        
        self.tool_panel_update()