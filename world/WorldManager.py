from __future__ import annotations

from world.WorldLoader import WorldLoader

from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QColor

from base.functions import safe_class

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from ui.GameWindow import GameWindow

@safe_class
class WorldManager:
    def __init__(self, window:GameWindow, tool_panel_update:Callable|None=None, resource_panel=None, initial:str|None=None, loader=WorldLoader):
        self.window = window
        self.loader = loader
        self.scene = window.scene
        self.view = window.view
        self.tool_panel_update = tool_panel_update
        self.current = None
        self.current_name = None
        self.overlay:QGraphicsRectItem|None = None

        self.resource_panel=resource_panel
        if initial is not None:
            self.switch_to(initial)

    def _create_overlay(self):
        self.overlay = QGraphicsRectItem(0, 0, self.current.sizeX*32, self.current.sizeY*32)
        self.overlay.setBrush(QColor(0, 0, 0, 255))
        self.overlay.setZValue(100)  
        self.scene.addItem(self.overlay)
        self.overlay.hide()

    def load(self, name):
        self.scene.clear()
        self._create_overlay()
        world = self.loader.load(name, scene=self.scene, view=self.view, window=self.window)
        if self.resource_panel is not None and world.Base is not None:
            world.Base.panel = self.resource_panel

        return world

    def save(self, name):
        if self.current is not None:
            return self.loader.save(self.current, name, view=self.view)

    def switch_to(self, name):
        if self.current is not None:
            self.save(self.current_name)

        if self.window.pause_menu.tree is not None:
            self.window.pause_menu.tree.update()

        self.current = self.load(name)
        self.current_name = name

        self.tool_panel_update()