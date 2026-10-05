from world.World import World
from world.WorldLoader import WorldLoader

from components.Storable import Storable
from enum import Enum, auto

import pyclr, applib, importlib, traceback, sys

from PyQt6.QtWidgets import QApplication
import base.font
import base.cursors
    
application = QApplication(sys.argv)
base.font.__dict__[...] = application
base.cursors.__dict__[...] = application

FULL_TESTS = []
SMOKE_TESTS = []

class Mode(Enum):
    SMOKE = auto()
    FULL = auto()

def full(func):
    FULL_TESTS.append(func)
    return func

def smoke(func):
    SMOKE_TESTS.append(func)
    return func

@full
def test_names(*a):
    def test(path):
        failed = []
        try:
            for module in applib.Storage(path).list():
                if not module.endswith(".py"):
                    continue
                name = module[:-3]
                mod = importlib.import_module(f"{path}.{name}")

                ex = mod.__dict__.get(module[:-3])
                if ex is None:
                    failed.append(f"The module <composites/{module}> lacks a final class")
            return failed
        except Exception as e:
            raise Exception(traceback.format_exc())
        
    failed = []      
    failed.extend(test("composites"))
    failed.extend(test("components"))
    failed.extend(test("ui"))
    failed.extend(test("world"))
    if failed:
        raise AssertionError(("\n---".join(failed)))

@smoke
def test_world(world:World):
    WorldLoader.save(world, "__TEST__")
    WorldLoader.load("__TEST__")
    WorldLoader.remove("__TEST__")

@smoke
def test_world_creates(world:World):
    assert world is not None
    assert world.sizeY > 0
    assert world.sizeX > 0

def start(mode:Mode) -> list:
    world = World(devmode=True)
    failed = []
    critical = []
    for func in SMOKE_TESTS:
        try:
            func(world)
        except AssertionError as e:
            failed.append(f"{func.__name__.replace("_", " ").title()}: {e}")
        except Exception:
            critical.append(f"{func.__name__.replace("_", " ").title()}: {traceback.format_exc()}")
            break

    if mode is Mode.FULL:
        for func in FULL_TESTS:
            try:
                func(world)
            except AssertionError as e:
                failed.append(f"{func.__name__.replace("_", " ").title()}: {e}")
            except Exception:
                critical.append(f"{func.__name__.replace("_", " ").title()}: {traceback.format_exc()}")
                break

    return failed, critical

if __name__ == "__main__":
    failed, critical = start(Mode.FULL)
    if critical:
        pyclr.cprint(f"Found {len(critical)} critical:", *critical, sep="\n---", style=pyclr.Bold, color="red")
    elif failed:
        pyclr.cprint(f"Found {len(failed)} failed tests:", *failed, sep="\n---", style=pyclr.Bold, color="red")
    else:
        pyclr.cprint("All systems online", style=pyclr.Bold, color="#2aa7f0")
        