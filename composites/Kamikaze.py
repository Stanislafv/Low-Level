from composites.Entity import Entity
from base.functions import save

import math

class Kamikaze(Entity):
    def __init__(self, *args, aimtype="base", damage=1, speedcoef=0.3, **kwargs):
        self.aimtype = aimtype
        self.damage = damage
        self.speedcoef = speedcoef
        self.aim = None
        super().__init__(*args, **kwargs)
        for block in self.w.blocks:
            if block.name == self.aimtype:
                self.aim = block

    @save
    def update(self, tick, dt):
        if super().update(tick) and self.aim is not None:
            if not self.aim.exists:
                return
            dx = self.aim.x - self.x
            dy = self.aim.y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            angle = math.degrees(math.atan2(dy, dx))
            
            if dist > 1:
                self.speed = (dx/dist*self.speedcoef, dy/dist*self.speedcoef)
                self.angle = angle
            else:
                self.aim.hp -= self.damage
                self.remove()
