from typing import Callable, Any, NoReturn

import applib, traceback
import base.folders as folders
from PyQt6.QtGui import QPixmap

TEXTURE_CACHE:dict[str, QPixmap] = {}
ANIMATION_CACHE:dict[str, QPixmap] = {}

def try_int(n):
    if int(n) == float(n):
        return int(n)
    return float(n)

def save(func:Callable) -> Callable[..., Any]:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if str((func.__qualname__, e)) not in save.errors:
                folders.folder.log.write(f"<{func.__qualname__}> - {traceback.format_exc()}", type="RuntimeError", set_error=True)
                save.errors.add(str((func.__qualname__, e)))
            else:
                applib.lprint(f"<{func.__qualname__}> - {e}", type="RuntimeError", set_error=True)
    return wrapper

save.errors = set()

@save
def get_texture(name) -> QPixmap:
    if name not in TEXTURE_CACHE:
        path = folders.textures.path(f"{name}.png")
        pixmap = QPixmap(path)
        if pixmap.isNull():
            folders.folder.log.write(f"Texture <{path}> not found", type="TextureCache")
            pixmap = QPixmap(folders.textures.path("404.png"))
        else:
            applib.lprint(f"Loaded: <{path}> ({pixmap.width()}x{pixmap.height()})", type="TextureCache")
        TEXTURE_CACHE[name] = pixmap
    
    return TEXTURE_CACHE[name]

class Meta(type):
    def __call__(self, *args, **kwargs) -> any:
        return self.__call__(*args, **kwargs)

    def __repr__(self):
        return repr(self.__init__())

class Static(metaclass=Meta):
    @classmethod
    def __call__(cls) -> NoReturn:
        raise AttributeError(f"type object '{cls.__name__}' has no attribute '__call__'")

    @classmethod
    def __init__(cls) -> NoReturn:
        raise AttributeError(f"type object '{cls.__name__}' has no attribute '__repr__'")

