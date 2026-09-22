from __future__ import annotations
import traceback, applib

from typing import Callable, TYPE_CHECKING
from base.folders import folder

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

from dataclasses import dataclass

@dataclass
class Task:
    ms:int
    func:Callable
    progress:float=0

class Updatable:
    def __init__(self, owner:SceneObject, tasks:list[tuple[int, Callable]]):
        self.owner = owner
        self.tasks:list[Task] = []
        for task in tasks:
            self.every(task[0], task[1])

    def every(self, ms:int, func:Callable):
        self.tasks.append(Task(ms, func))
        return self

    def __call__(self, dt):
        for task in self.tasks:
            task.progress += dt
            while task.progress >= task.ms:
                task.progress -= task.ms
                try:
                    task.func(self.owner)
                except Exception:
                    folder.log.write(traceback.format_exc(1), type=applib.ERROR)
                    break