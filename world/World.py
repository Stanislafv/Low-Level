from __future__ import annotations

from composites.Block import Block
from composites.Entity import Entity

from base.composites import composites
from base.MusicPlayer import MusicPlayer
from base.folders import folder, block_config, entity_config, saves

from components.Clickable import Clickable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable
from components.Storable import Storable

from PyQt6.QtWidgets import QGraphicsItem

from world.TempField import TempField

import applib, random, os, json

from typing import TYPE_CHECKING, Literal, cast
if TYPE_CHECKING:
    from components.SceneObject import SceneObject
    from composites.StorageBlock import StorageBlock

    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

class World:
    def __init__(self, sizeX=256, sizeY=256, scene:QGraphicsScene|None=None, devmode:bool=folder.config["devmode"], temperature=20):
        self.sizeX = sizeX
        self.sizeY = sizeY

        self.team = "PlayerTeam"

        self.blocks:list[Block] = []
        self.block_map:dict[tuple[int, int], list[Block]] = {}

        self.entities:list[Entity] = []
        self.entity_map:dict[tuple[int, int], Entity] = {}

        self.Base:StorageBlock = None
        self.devmode = devmode

        self.relief_map:None|QGraphicsPixmapItem  = None

        self.temperature = TempField(sizeY, sizeX, temperature)

        self.placing_block:str = "drill"
        self.opened:list[str] = ["drill", "conveyor_down", "conveyor_up", "conveyor_left", "conveyor_right"]

        self.scene = scene

    def update(self, dt):
        folder.plugins.call("update", dt)

        for block in self.blocks.copy():
            if Updatable in block.components:
                block.components[Updatable](dt*1000)
            
        for entity in self.entities.copy():
            if Updatable in entity.components:
                entity.components[Updatable](dt*1000)

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

    def click(self, type:Literal["left", "right"], x, y) -> None:
        if type == "left":
            existing = self.get_block_at(x, y)
            if existing and block_config[existing.name]["z"] >= 20:
                if Clickable in existing.components:
                    existing.components[Clickable]()

            else:  
                type_name = None
                cost = None
        
                if self.placing_block in block_config:
                    type_name = block_config[self.placing_block].get("type")
                    cost = block_config[self.placing_block].get("cost")
        
                if self.placing_block in entity_config:
                    type_name = entity_config[self.placing_block].get("type")
                    cost = entity_config[self.placing_block].get("cost")
        
                block_class = composites.get(type_name)
                if block_class is None:
                    folder.log.write(f"Class <{type_name}> not exists", type=applib.ERROR)
                    return
        
                if cost is not None and self.Base is not None:
                    for name, value in cost.items():
                        coef = folder.config.get("craft_coef", 1)
                        if not self.Base.components[Storable].reduce(name, int(value*coef)):
                            return
                                    
                obj:SceneObject = block_class(self, x, y, self.placing_block, team=self.team)
                if Placable in obj.components:
                    obj.components[Placable]()
                
        elif type == "right":
            existing = self.get_block_at(x, y)
            if existing:            
                self.remove_block(existing)
        else:
            raise Exception("а обработать её а")

    def get_block_at(self, x, y) -> Block|None:
        blocks = self.block_map.get((x, y), None)
        if blocks is not None:
            return max(blocks, key=lambda ex: block_config[ex.name]["z"])
        return []

    def load(self, name):
            if not os.path.exists(saves.path(name)):
                folder.log.write(f"File of sector not found", type="LoadError")
            MusicPlayer.play("load")
            for block in self.blocks:
               self.remove_block(block)
    
            sector_path = saves.mkdir(name)
    
            if os.path.exists(sector_path.path("ReliefMap.png")):
                pixmap = QPixmap(sector_path.path("ReliefMap.png"))
    
                self.relief_map = self.scene.addPixmap(pixmap)
                self.relief_map.setPos(0, 0)
                self.relief_map.setZValue(0)
                self.relief_map.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
    
            config = sector_path.read("config.json", "json")
    
            self.temperature = TempField(config.get("sizeY", 256), config.get("sizeX", 256))
    
            if config.get("version") != folder.version:
                folder.log.write(f"Different save versions", type="LoadWarning")
    
            try:
                for b in sector_path.read("Blocks.json", type="json"):
                    a = b.copy()
                    block_type_name = a.pop("type")
                    
                    block_class = composites[block_type_name]
                    block_class(self, **a)
    
            except (json.JSONDecodeError, KeyError) as e:
                folder.log.write(f"Error reading the sector file: <{e}>", type="LoadError", set_error=True)
    
            self.save_name = name

