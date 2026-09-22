from composites.PowerBlock import PowerBlock, Block

class Peltier(PowerBlock):
    def __init__(self, *args, **kwargs):
        self._time_after = 0
        super().__init__(*args, **kwargs)

    def update(self, tick, dt):
        self._time_after += dt
        if self._time_after > 1:
            left:Block = self.w.get_block_at(self.x-1, self.y)
            right:Block = self.w.get_block_at(self.x+1, self.y)
            if left is not None and right is not None:                         
                if left.temperature != right.temperature:
                    self.energy += abs(left.temperature-right.temperature) * 0.05

            super().update(tick, dt)
            