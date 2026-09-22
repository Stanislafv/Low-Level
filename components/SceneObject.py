from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING, TypeVar, Type
if TYPE_CHECKING:
    from ui.GameWindow import GameWindow

T = TypeVar("T")

class ComponentDict(dict[type, object]):
    def __getitem__(self, key: Type[T]) -> T:
        return super().__getitem__(key) 

@dataclass
class SceneObject:
    w:GameWindow
    x:int|float
    y:int|float
    name:str
    team:str

    components:ComponentDict[Type[T], Type[T]] = field(default_factory=ComponentDict)
    exists:bool=True

    def __repr__(self):
        return f"<{type(self).__name__}>"
