from composites.Block import Block

from base.cursors import Cursor

class MemoryBlock(Block):
    def __init__(self, *args, **kwargs):
        self.variables = {}
        self.max_memory = 8
        self.memory = 0

        super().__init__(*args, **kwargs)

    def on_click(self):
        print(self.variables)

    def draw(self):
        super().draw()
        self.pixmap_item.setCursor(Cursor.Hand)