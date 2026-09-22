import os, json, traceback
from datetime import datetime

from base.MusicPlayer import MusicPlayer
from base.folders import folder, saves, block_config

from base.composites import composites
from base.components import components

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPixmap

from components.Storable import Storable

from world.TempField import TempField
from world.World import World

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from composites.Block import Block
    
class WorldLoadError(Exception): ...

class WorldLoader:
    @staticmethod
    def load(name, scene=None) -> World | None: 
            if not os.path.exists(saves.path(name)):
                folder.log.write(f"File of sector <{name}> not found", type="LoadError", set_error=1)
                raise WorldLoadError(f"File of sector <{name}> not found")

            sector_path = saves.mkdir(name)
            config:dict = sector_path.read("config.json", "json")

            if config.get("version") != folder.version:
                folder.log.write(f"Different save versions", type="LoadWarning")
            
            world = World(config.get("sizeX", 256), config.get("sizeY", 256), scene=scene)

            for block in world.blocks.copy():
                world.remove_block(block)

            world.opened = config.get("opened", [])

            world.temperature = TempField(config.get("sizeX", 256), config.get("sizeY", 256), ambient=config.get("ambient", 0))
            world.temperature.load(name)
    
            if os.path.exists(sector_path.path("ReliefMap.png")) and world.scene is not None:
                pixmap = QPixmap(sector_path.path("ReliefMap.png"))
    
                world.relief_map = world.scene.addPixmap(pixmap)
                world.relief_map.setPos(0, 0)
                world.relief_map.setZValue(0)
                world.relief_map.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
    
            try:
                for block in sector_path.read("Blocks.json", type="json"):
                    try:
                        block_class = composites[block_config[block["name"]]["type"]]
                    except KeyError as e:
                        folder.log.write(f"Invalid composite settings KeyError: <{e}>")
                        continue

                    block_сам:Block = block_class(world, name=block["name"], x=block["x"], y=block["y"], team="PlayerTeam")
                    if block["name"] == "base":
                        world.Base = block_сам

                    for name, value in block.items():
                        if isinstance(value, dict):
                            for st, zn in value.items():
                                try:
                                    cls = components[name]
                                    block_сам.components[cls].__setattr__(st, zn)
                                except KeyError:
                                    folder.log.write(f"Invalid component <{name}>", type="LoadError", set_error=True)
    
            except (json.JSONDecodeError, KeyError) as e:
                folder.log.write(f"Error reading the sector file: <{traceback.format_exc()}>", type="LoadError", set_error=True)
            else:
                return world

    @staticmethod
    def save(world:World, name):
            try:
                if not os.path.exists(saves.path(name)):
                    folder.log.write(f"File of sector not found", type="SaveError")
        
                blocks = []
        
                sector_path = saves.mkdir(name)
                
                for block in world.blocks:
                    if not block.exists:
                        continue
                
                    entry = {"x": block.x, "y": block.y, "name": block.name}
                    for atr, value in block.components.items():
                        if hasattr(atr, "save"):
                            entryf = {}
                            for a in atr.save:
                                try:
                                    b = value.__getattribute__(a)
                                except AttributeError:
                                    folder.log.write(f"Storable components has no attribute <{a}>")
                                    continue
                                if type(b) == tuple:
                                    b = list(b)
                                try:
                                    json.dumps(b)
                                except Exception: pass
                                else:
                                    entryf[a] = b
                            entry[atr.__name__] = entryf
                
                    if not block_config[block.name].get("relief", False):
                        blocks.append(entry)
                
                current_time = datetime.now()

                world.temperature.save(name)

                config = {"version": folder.version, "time": current_time.strftime("[%Y-%m-%d] %H:%M"),
                        "ambient": world.temperature.ambient, "sizeX": world.sizeX, "sizeY": world.sizeY,
                        "opened": world.opened}
                
                sector_path.write("Blocks.json", blocks, type="json")
                sector_path.write("config.json", config, type="json")
            except Exception:
                traceback.print_exc()

    @staticmethod
    def remove(name):
        world = saves.mkdir(name)
        world.destroy()
