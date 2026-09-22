from composites.Entity import Entity
from composites.Block import Block
from composites.Missile import Missile
from base.functions import get_texture

import math

class Turrel(Block):
    def __init__(self, w, x:int, y:int, name:str, team:str, **kwargs):
        pixmap = get_texture(name)
        super().__init__(w, x, y, f"turrel_base({pixmap.width()}x{pixmap.height()})", team=team, **kwargs)
        self.type = "None"
        
        self.team = team
        self.target = None

        if self.place():
            self.tower = Entity(w, x, y, name=name, team=team, can_damage=False)

            self.hp = self.tower.states["hardness"]
            self.speedcoef = self.tower.states["speedcoef"]
            self.damage = self.tower.states["damage"]
            self.reloading = self.tower.states["reloading"]
            self.radius = self.tower.states["radius"]
            self.missile = self.tower.states["missile"]
        else:
            self.remove()

    def on_click(self):
        print("123")

    def remove(self):
        if hasattr(self, "tower"):
            self.tower.remove()
        super().remove()

    def find_target(self):
        self.target = None
        smallest_dist = float("inf")
        
        for entity in self.w.entities:
            if not entity.exists:
                continue
            if entity.team == self.team:
                continue
            
            dx = entity.x - self.x
            dy = entity.y - self.y
            dist = abs(dx*dx + dy*dy)
            
            if dist < smallest_dist and dist <= self.radius:
                smallest_dist = dist
                self.target = entity
        
        return self.target

    def update(self, tick, dt): 
        if not self.tower.exists:
            return
        if tick % self.reloading == 0:
            self.find_target()
        if tick % self.reloading == 0 and self.target is not None:
            if not self.target.exists:
                return
            
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = abs(dx*dx + dy*dy) ** 0.5

            self.tower.angle = math.degrees(math.atan2(dy, dx)) + 90
            
            if dist > 0:
                Missile(
                    w=self.w,
                    x=self.x,
                    y=self.y,
                    team=self.team,
                    name=self.missile,
                    speed=(dx/dist*self.speedcoef, dy/dist*self.speedcoef),
                    damage=self.damage
                    )
