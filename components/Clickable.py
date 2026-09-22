from __future__ import annotations
import traceback, applib

from typing import Callable, TYPE_CHECKING
from base.cursors import Cursor
from base.folders import folder

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Clickable:
    def __init__(self, owner:SceneObject, func:Callable):
        self.owner = owner
        self.func = func

        if hasattr(owner, "pixmap_item"):
            owner.pixmap_item.setCursor(Cursor.Hand)

    def __call__(self):
        try:
            self.func(self.owner)
        except Exception as e:
            folder.log.write(traceback.format_exc(1), type=applib.ERROR)
            