import applib
import base.folders as folders
from base.functions import save, get_texture

entities = folders.mainfolder.read("entity_config.json", type="json")

class Entity:
    def __init__(self, w, x, y, name:str, team, angle:float=0, speed:tuple=(0, 0), can_damage=True, states:dict=None, *args, **kwargs):
        self.w=w
        self.name=name
        self.x=x
        self.y=y
        self.angle = angle
        self.speed = speed
        self.team = team
        self.can_damage = can_damage
        self.old_x = None
        self.old_y = None
        self.old_angle = None
        self.exists = True
        if states is not None:
            self.states = states
        else:
            self.states = entities.get(self.name, None)
        if self.states is None:
            applib.lprint(f"States for {self} not found in <{folders.mainfolder.path("entity_config.json")}>")
            self.states = entities["404"]
        self.type = self.states["type"]
        self._hp = self.states.get("hardness", 1)
        self.w.entities.add(self)

        self.pixmap = get_texture(self.name)
        self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
        self.pixmap_item.setTransformOriginPoint(self.pixmap.width() / 2, self.pixmap.height()  / 2)
        self.pixmap_item.setZValue(40)

    @save
    def update(self, tick, dt):
        if self._hp <= 0:
            self.remove()
            return False
        self.x+=self.speed[0] * dt * 60
        self.y+=self.speed[1] * dt * 60
        if self.x == self.old_x and self.y == self.old_y and self.angle == self.old_angle:
            return False
        if self.x != self.old_x or self.y != self.old_y:
            self.pixmap_item.setPos(self.x*32, self.y*32)
        if self.old_angle != self.angle:
            self.pixmap_item.setRotation(self.angle)
        self.old_x = self.x
        self.old_y = self.y
        self.old_angle = self.angle
        return True

    @property
    def hp(self) -> float|int:
        return self._hp
    
    @hp.setter
    def hp(self, f):
            if self._hp == -1:
                return
            if f <= 0:
                self.remove()
            self._hp = f

    def get_occupied_cells(self):
        cells = set()
        width_tiles = self.pixmap_item.pixmap().width() // 32
        height_tiles = self.pixmap_item.pixmap().height() // 32
        
        for dx in range(width_tiles):
            for dy in range(height_tiles):
                cells.add((int(self.x) + dx, int(self.y) + dy))
        return cells

    def get_around(self):
        cells = set()
        for cell in self.get_occupied_cells():
            for coef in ((1, 0), (-1, 0), (0, 1), (0,-1)):
                cells.add((cell[0]+coef[0], cell[1]+coef[1]))
        return cells 

    @save
    def get_collide(self):
        for entity in self.w.entities:
            if entity is self or entity.team == self.team:
                continue
            for x, y in entity.get_around():
                if x == round(self.x) and y == round(self.y):
                    return entity
        for block in self.w.blocks:
            if block.team == self.team:
                continue
            for x, y in block.get_around():
                if x == round(self.x) and y == round(self.y):
                    return block

    @save
    def remove(self, sound=True):
        if not self.exists:
            return
        self.exists = False
        if hasattr(self, 'pixmap_item'):
            self.w.scene.removeItem(self.pixmap_item)
            self.w.scene.update()
        if self in self.w.entities:
            self.w.entities.remove(self)

    def __repr__(self):
        output = ""
        for name, value in self.__dict__.items():
            output += f"{name}: {value}, "
        return f"<{type(self).__name__}({output[:-2]})>"