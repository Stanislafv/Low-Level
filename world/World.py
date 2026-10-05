from __future__ import annotations

from composites.Block import Block
from composites.Unit import Unit

from base.composites import composites
from base.MusicPlayer import MusicPlayer
from base.folders import folder, block_config, unit_config
from base.functions import safe_class

from components.Clickable import Clickable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable
from components.Storable import Storable

from world.TempField import TempField

import applib, random
from functools import partialmethod

from typing import TYPE_CHECKING, Literal, cast
if TYPE_CHECKING:
    from components.SceneObject import SceneObject
    from composites.StorageBlock import StorageBlock
    from composites.Unit import Unit

    from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

@safe_class
class World:
    def __init__(self, sizeX=256, sizeY=256, scene:QGraphicsScene|None=None, window=None, devmode:bool=folder.config["devmode"], temperature=20):
        self.sizeX = sizeX
        self.sizeY = sizeY

        self.window = window

        self.blocks:list[Block] = []
        self.block_map:dict[tuple[int, int], list[Block]] = {}

        self.units:list[Unit] = []
        self.unit_map:dict[tuple[int, int], list[Unit]] = {}

        self.Base:StorageBlock = None
        self.devmode = devmode

        self.relief_map:None|QGraphicsPixmapItem  = None

        self.temperature = TempField(sizeY, sizeX, temperature)

        self.placing_block:str = None
        self.opened:list[str] = ["drill", "conveyor_down", "conveyor_up", "conveyor_left", "conveyor_right"]

        self.scene = scene

    def update(self, dt):
        folder.plugins.call("update", dt)

        for block in self.blocks.copy():
            if Updatable in block.components:
                block.components[Updatable](dt*1000)
            
        for unit in self.units.copy():
            if Updatable in unit.components:
                unit.components[Updatable](dt*1000)

        self.temperature.update(dt)

    def remove_block(self, block:Block):
        if block in self.blocks:
            self.blocks.remove(block)

        for xcoord, ycoord in block.get_occupied_cells():
            if (xcoord, ycoord) in self.block_map:
                blocks = cast(list[Block], self.block_map.get((xcoord, ycoord)))
                if block in blocks:
                    blocks.remove(block)
                if len(blocks) == 0:
                    del self.block_map[(xcoord, ycoord)]

        if not self.devmode:
            cost:dict = block_config[block.name].get("cost")
            coef = folder.config.get("craft_coef", 1)
            if cost is not None and self.Base is not None:
                for name, value in cost.items():
                    self.Base.components[Storable].add(name, int(value*coef))

        if not self.devmode and block_config[block.name]["z"] < 20:
            return
        
        if Removable in block.components:
            block.components[Removable]()
                        
        block.exists = False
        if hasattr(block, 'pixmap_item'):
            MusicPlayer.play(random.choice(["destruction_1", "destruction_2"]), volume=0.7)
            scene = block.pixmap_item.scene()
            scene.removeItem(block.pixmap_item)
            scene.update()

    def append_block(self, block:Block):
        self.blocks.append(block)

        for xcoord, ycoord in block.get_occupied_cells():
            if (blocks:=self.block_map.get((xcoord, ycoord))) is not None:
                self.block_map[(xcoord, ycoord)] = [block, *blocks]
                continue
            self.block_map[(xcoord, ycoord)] = [block]

    def append_unit(self, unit:Unit):
        self.units.append(unit)

        for xcoord, ycoord in unit.get_occupied_cells():
            if (units:=self.unit_map.get((xcoord, ycoord))) is not None:
                self.unit_map[(xcoord, ycoord)] = [unit, *units]
                continue
            self.unit_map[(xcoord, ycoord)] = [unit]

    def click(self, type:Literal["left", "right"], x, y) -> None:
        if type == "left":
            existing = self.get_block_at(x, y)
            if existing and block_config[existing.name]["z"] >= 20:
                if Clickable in existing.components:
                    existing.components[Clickable]()
            else:  
                type_name = None
                cost = None

                if self.placing_block is None:
                    return
        
                if self.placing_block in block_config:
                    type_name = block_config[self.placing_block].get("type")
                    cost = block_config[self.placing_block].get("cost")
        
                if self.placing_block in unit_config:
                    type_name = unit_config[self.placing_block].get("type")
                    cost = unit_config[self.placing_block].get("cost")
        
                block_class = composites.get(type_name)
                if block_class is None:
                    folder.log.write(f"Class <{type_name}> not exists", type=applib.ERROR)
                    return
        
                if cost is not None and self.Base is not None:
                    for name, value in cost.items():
                        coef = folder.config.get("craft_coef", 1)
                        if not self.Base.components[Storable].reduce(name, int(value*coef)):
                            return
                                    
                obj:SceneObject = block_class(self, x, y, self.placing_block)
                if Placable in obj.components:
                    obj.components[Placable]()
                
        elif type == "right":
            existing = self.get_block_at(x, y)
            if existing:            
                self.remove_block(existing)
        else:
            raise Exception(f"type <{type}> has no handler")

    def get_block_at(self, x, y) -> Block|None:
        blocks = self.block_map.get((x, y), None)
        if blocks is not None:
            return max(blocks, key=lambda ex: block_config[ex.name]["z"])
        return []

    place = partialmethod(click, "left")
    remove = partialmethod(click, "right")
