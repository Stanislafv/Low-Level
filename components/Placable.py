from __future__ import annotations
import traceback, applib

from typing import Callable, TYPE_CHECKING
from base.folders import folder

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Placable:
    def __init__(self, owner:SceneObject, func:Callable):
        self.owner = owner
        self.func = func

    def __call__(self):
        try:
            self.func(self.owner)
        except Exception as e:
            folder.log.write(traceback.format_exc(), type=applib.ERROR)