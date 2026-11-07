class World:
    def __init__(self):
        self.blocks = set()
        self.blocks2 = {}

    def add(self, pos, kind):
        self.blocks.add(pos)
        self.blocks2[pos] = kind

    def remove(self, pos):
        self.blocks.discard(pos)

    def has(self, pos):
        return pos in self.blocks