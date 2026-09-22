from composites.Entity import Entity
from base.functions import save

class Missile(Entity):
    def __init__(self, *args, team, damage=0.1, min_z=20, live_time=300, parent=None, **kwargs):
        self.damage = damage
        self.min_z = min_z
        self.parent = parent
        self.team = team
        self.start_tick = None
        self.live_time = live_time
        if "can_damage" in kwargs:
            del kwargs["can_damage"]
        super().__init__(can_damage=False, team=team, states={"type": "Entity", "hardness": 1}, *args, **kwargs)

    @save
    def update(self, tick, dt):
        super().update(tick, dt)
        if self.start_tick is None:
            self.start_tick = tick
        else:
            if tick-self.start_tick > self.live_time:
                self.remove()
                return
        if (block:=self.get_collide()) is not None:
            if block.states.get("z", 40) >= self.min_z:
                block.hp -= self.damage
                self.remove()
