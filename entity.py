import math
from rect3 import *

class Block:
    def __init__(self, x, y, z, fx, fy, fz, kind):
        self.rect = EntityRect(x, y, z, 0.4, 0.4, 0.4)
        self.vx = fx
        self.vy = fy
        self.vz = fz
        self.kind = kind
        self.on_ground = False
        self.gravity = 25
    def update(self, world, dt):
        steps = math.ceil(dt / 0.01)
        dt /= steps

        for _ in range(steps):
            blocks = world.blocks
            # ---------------- X축 ----------------
            self.rect.x += self.vx * dt

            for block in blocks:
                rect = block_rect(block)
                if self.rect.colliderect(rect):

                    # 오른쪽으로 이동 중
                    if self.vx > 0:
                        self.rect.x = rect.left - self.rect.width / 2

                    # 왼쪽으로 이동 중
                    elif self.vx < 0:
                        self.rect.x = rect.right + self.rect.width / 2

            # ---------------- Z축 ----------------
            self.rect.z += self.vz * dt

            for block in blocks:
                rect = block_rect(block)
                if self.rect.colliderect(rect):

                    if self.vz > 0:
                        self.rect.z = rect.front - self.rect.depth / 2

                    elif self.vz < 0:
                        self.rect.z = rect.back + self.rect.depth / 2

            # ---------------- Y축 ----------------
            self.vy -= self.gravity * dt

            self.rect.y += self.vy * dt


            self.on_ground = False

            for block in blocks:
                rect = block_rect(block)
                if self.rect.colliderect(rect):

                    if self.vy < 0:
                        self.rect.y = rect.top
                        self.vy = 0
                        self.on_ground = True

                    elif self.vy > 0:
                        self.rect.y = rect.bottom - self.rect.height
                        self.vy = 0

    @property
    def faces(self):
        return [
            [(4, 5, 6, 7), "side"],    # +Z
            [(0, 1, 2, 3), "side"],   # -Z
            [(1, 5, 6, 2), "side"],    # +X
            [(0, 4, 7, 3), "side"],   # -X
            [(3, 2, 6, 7), "top"],     # +Y (윗면)
            [(0, 1, 5, 4), "bottom"] # -Y (아랫면)
        ]

    @property
    def verticals(self):
        return [
            (self.x - 0.2, self.y - 0.2, self.z - 0.2),  # 0
            (self.x + 0.2, self.y - 0.2, self.z - 0.2),  # 1
            (self.x + 0.2, self.y + 0.2, self.z - 0.2),  # 2
            (self.x - 0.2, self.y + 0.2, self.z - 0.2),  # 3
            (self.x - 0.2, self.y - 0.2, self.z + 0.2),  # 4
            (self.x + 0.2, self.y - 0.2, self.z + 0.2),  # 5
            (self.x + 0.2, self.y + 0.2, self.z + 0.2),  # 6
            (self.x - 0.2, self.y + 0.2, self.z + 0.2),  # 7
        ]

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def z(self):
        return self.rect.z