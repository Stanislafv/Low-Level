from __future__ import annotations

from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem

import base.folders as folders
import base.functions as func

import json, os
from datetime import datetime

from base.composites import composites
from base.MusicPlayer import MusicPlayer
from base.folders import block_config

from components.Storable import Storable

from world.TempField import TempField

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.World import World

class SectorManager:
    @func.save
    @staticmethod
    def save_editor(window:World, name):
        pixmap = QPixmap(window.sizeX*32, window.sizeY*32)
        painter = QPainter(pixmap)

        painter.fillRect(0, 0, window.sizeX*32, window.sizeY*32, QBrush(QColor(30, 30, 30)))

        sector_path = folders.saves.mkdir(name)

        blocks_relief = []
        blocksf = []

        for block in window.blocks:
            if not block.exists:
                continue

            entry = {}
            for atr, value in block.__dict__.items():
                if type(value) == tuple:
                    value = list(value)
                try:
                    json.dumps(value)
                except Exception: pass
                else:
                    entry[atr] = value

            if block_config[block.name].get("relief", False):
                painter.drawPixmap(int(block.pixmap_item.x()), int(block.pixmap_item.y()), block.pixmap)

                blocks_relief.append(entry)
            else:
                blocksf.append(entry)

        painter.end()

        current_time = datetime.now()
        config = {"version": folders.folder.version, "time": current_time.strftime("[%Y-%m-%d] %H:%M")}

        sector_path.write("ReliefBlocks.json", blocks_relief, type="json")
        sector_path.write("Blocks.json", blocksf, type="json")
        sector_path.write("config.json", config, type="json")

        pixmap.save(sector_path.path("ReliefMap.png"), "png")

        pixmap.scaled(256, 256).save(sector_path.path("ViewMap.png"), "png")

    @func.save
    @staticmethod
    def save(window:World, name):
        if not os.path.exists(folders.saves.path(name)):
            folders.folder.log.write(f"File of sector not found", type="SaveError")

        blocks = []

        sector_path = folders.saves.mkdir(name)
        
        for block in window.blocks[1:]:
            if not block.exists:
                continue
        
            entry = {}
            for atr, value in block.__dict__.items():
                        if type(value) == tuple:
                            value = list(value)
                        try:
                            json.dumps(value)
                        except Exception: pass
                        else:
                            entry[atr] = value
        
            if not block_config[block.name].get("relief", False):
                blocks.append(entry)
        
        current_time = datetime.now()
        config = {"version": folders.folder.version, "time": current_time.strftime("[%Y-%m-%d] %H:%M"), "base_storage": window.Base.components[Storable].dict()}
        
        sector_path.write("Blocks.json", blocks, type="json")
        sector_path.write("config.json", config, type="json")
    
    @func.save
    @staticmethod
    def load_editor(window:World, name):
        if not os.path.exists(folders.saves.path(name)):
            folders.folder.log.write(f"File of sector not found", type="LoadError")

        for block in window.blocks:
            window.remove_block(block)

        sector_path = folders.saves.mkdir(name)

        if sector_path.read("config.json", "json").get("version") != folders.folder.version:
            folders.folder.log.write(f"Different save versions", type="LoadWarning")

        for fname in ["ReliefBlocks", "Blocks"]:
            for b in sector_path.read(f"{fname}.json", type="json"):
                a = b.copy()
                block_type_name = a.pop("type")
                            
                block_class = composites[block_type_name]
                            
                if hasattr((obj:=block_class(window, **a)), "place"):
                    obj.place()

    @func.save
    @staticmethod
    def load(window:World, name):
        if not os.path.exists(folders.saves.path(name)):
            folders.folder.log.write(f"File of sector not found", type="LoadError")
        MusicPlayer.play("load")
        for block in window.blocks:
            window.remove_block(block)

        sector_path = folders.saves.mkdir(name)

        if os.path.exists(sector_path.path("ReliefMap.png")):
            pixmap = QPixmap(sector_path.path("ReliefMap.png"))

            window.relief_map = window.scene.addPixmap(pixmap)
            window.relief_map.setPos(0, 0)
            window.relief_map.setZValue(0)
            window.relief_map.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

        config = sector_path.read("config.json", "json")

        window.temperature = TempField(config.get("sizeY", 256), config.get("sizeX", 256))

        if config.get("version") != folders.folder.version:
            folders.folder.log.write(f"Different save versions", type="LoadWarning")

        try:
            for b in sector_path.read("Blocks.json", type="json"):
                a = b.copy()
                block_type_name = a.pop("type")
                
                block_class = composites[block_type_name]
                block_class(window, **a)

        except (json.JSONDecodeError, KeyError) as e:
            folders.folder.log.write(f"Error reading the sector file: <{e}>", type="LoadError", set_error=True)

        window.save_name = name

    @func.save
    @staticmethod
    def clear(window:World):
        for block in window.blocks[1:]:
            window.remove_block(block)

        if hasattr(window, "relief_map"):
            window.scene.removeItem(window.relief_map)