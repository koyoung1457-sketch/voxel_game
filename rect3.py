import numpy as np

class BlockRect:
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z

        self.width = width
        self.height = height
        self.depth = depth

    def colliderect(self, other):
        return (
            self.left < other.right and
            self.right > other.left and

            self.bottom < other.top and
            self.top > other.bottom and

            self.front < other.back and
            self.back > other.front
        )

    @property
    def left(self):
        return self.x - self.width / 2

    @property
    def right(self):
        return self.x + self.width / 2

    @property
    def bottom(self):
        return self.y - self.height / 2

    @property
    def top(self):
        return self.y + self.height / 2

    @property
    def front(self):
        return self.z - self.depth / 2

    @property
    def back(self):
        return self.z + self.depth / 2

    @property
    def pos(self):
        return np.array([self.x, self.y, self.z])

    @pos.setter
    def pos(self, other):
        self.x = other[0]
        self.y = other[1]
        self.z = other[2]
class EntityRect:
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z

        self.width = width
        self.height = height
        self.depth = depth

    def colliderect(self, other):
        return (
            self.left < other.right and
            self.right > other.left and

            self.bottom < other.top and
            self.top > other.bottom and

            self.front < other.back and
            self.back > other.front
        )

    @property
    def left(self):
        return self.x - self.width / 2

    @property
    def right(self):
        return self.x + self.width / 2

    @property
    def bottom(self):
        return self.y

    @property
    def top(self):
        return self.y + self.height

    @property
    def front(self):
        return self.z - self.depth / 2

    @property
    def back(self):
        return self.z + self.depth / 2

    @property
    def pos(self):
        return np.array([self.x, self.y, self.z])

    @pos.setter
    def pos(self, other):
        self.x = other[0]
        self.y = other[1]
        self.z = other[2]
def block_rect(block):
    return BlockRect(block[0], block[1], block[2], 1, 1, 1)
