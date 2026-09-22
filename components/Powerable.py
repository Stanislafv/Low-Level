from __future__ import annotations

import PyQt6.QtGui as QtGui
from PyQt6.QtGui import QColor

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Powerable:
    save = ("energy",)
    def __init__(self, owner:SceneObject, max_energy:float|int):
        self.owner = owner

        self.parents:list[Powerable] = []
        self.max_energy = max_energy
        self.lines = set()
        self.energy = 0

    @staticmethod
    def place(obj:SceneObject):
        for block in obj.w.blocks:
            if block is obj:
                continue
            if Powerable in block.components:
                if (abs(block.x-obj.x)**2)+(abs(block.y-obj.y)**2) <= 75:
                    obj.components[Powerable].parents.append(block)
                    block.components[Powerable].parents.append(obj)
                    line = obj.w.scene.addLine((block.x+block.size[0]/2)*32, (block.y+block.size[1]/2)*32, (obj.x+obj.size[0]/2)*32, (obj.y+obj.size[0]/2)*32, QtGui.QPen(QColor(255, 255, 0), 5))
                    line.setZValue(40)
                    line.setOpacity(max(min(obj.components[Powerable].energy/0.1, 1), 0.1))
                    obj.components[Powerable].lines.add(line)
                    block.components[Powerable].lines.add(line)
        return True

    @staticmethod
    def remove(obj:SceneObject):
        for line in obj.components[Powerable].lines:
            obj.w.scene.removeItem(line)
        for block in obj.components[Powerable].parents:
            block.components[Powerable].parents.remove(obj)
            for line in obj.components[Powerable].lines:
                block.components[Powerable].lines.discard(line)
        obj.components[Powerable].energy = 0
        obj.components[Powerable].parents = set()
        return True

    @staticmethod
    def update(obj:SceneObject):
        for block in obj.components[Powerable].parents:
            if block.components[Powerable].energy < obj.components[Powerable].energy:
                energy = (obj.components[Powerable].energy-block.components[Powerable].energy)/2
                energy = min(energy, block.components[Powerable].max_energy-block.components[Powerable].energy)
                block.components[Powerable].energy += energy
                obj.components[Powerable].energy -= energy
        opacity = max(min(obj.components[Powerable].energy/0.1, 0.9), 0.1)
        for line in obj.components[Powerable].lines:
            line.setOpacity(opacity)
        return True