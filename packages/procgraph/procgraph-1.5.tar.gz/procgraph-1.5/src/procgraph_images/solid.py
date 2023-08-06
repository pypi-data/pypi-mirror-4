from procgraph import Block
import numpy as np
from procgraph import ETERNITY


class Solid(Block):
    Block.alias('solid')
    Block.output('rgb')
    Block.config('width')
    Block.config('height')
    Block.config('color')

    def update(self):
        rgb = solid(self.config.width, self.config.height, self.config.color)
        self.set_output(0, rgb, timestamp=ETERNITY)


def solid(width, height, color):
    rgb = np.zeros((height, width, 3), dtype='uint8')
    for i in range(3):
        rgb[:, :, i] = color[i]
    return rgb

