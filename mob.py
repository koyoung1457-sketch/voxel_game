import rect3
import math3
import math
import numpy as np

class Follower:
    def __init__(self, x, y, z):
        self.rect = rect3.EntityRect(x, y, z, 1, 1, 1)
        self.yaw, self.pitch = 0, 0
        self.speed = 3
        self.jump_speed = 8
        self.on_ground = False
        self.dx, self.dy, self.dz = 0, 0, 0
        self.find = False
        self.kind = "follower"

    def move(self, player):
        if np.linalg.norm((self.rect.pos-player.pos)[[0, 2]]) < 5:
            self.yaw, _ = math3.look_at(self.rect.pos, player.pos)
            self.find = True
        else:
            self.find = False
        if self.find:
            self.dx = math.sin(self.yaw) * self.speed
            self.dz = math.cos(self.yaw) * self.speed
        else:
            self.dx, self.dz= 0, 0

    def update(self, world, dt, gravity):
        blocks = world.blocks
        # ---------------- X축 ----------------
        self.rect.x += self.dx * dt

        for block in blocks:
            rect = rect3.block_rect(block)
            if self.rect.colliderect(rect):

                # 오른쪽으로 이동 중
                if self.dx > 0:
                    self.rect.x = rect.left - self.rect.width / 2
                    self.jump()

                # 왼쪽으로 이동 중
                elif self.dx < 0:
                    self.rect.x = rect.right + self.rect.width / 2
                    self.jump()

        # ---------------- Z축 ----------------
        self.rect.z += self.dz * dt

        for block in blocks:
            rect = rect3.block_rect(block)
            if self.rect.colliderect(rect):

                if self.dz > 0:
                    self.rect.z = rect.front - self.rect.depth / 2
                    self.jump()

                elif self.dz < 0:
                    self.rect.z = rect.back + self.rect.depth / 2
                    self.jump()

        # ---------------- Y축 ----------------
        self.dy -= gravity * dt

        self.rect.y += self.dy * dt


        self.on_ground = False

        for block in blocks:
            rect = rect3.block_rect(block)
            if self.rect.colliderect(rect):

                if self.dy < 0:
                    self.rect.y = rect.top
                    self.dy = 0
                    self.on_ground = True

                elif self.dy > 0:
                    self.rect.y = rect.bottom - self.rect.height
                    self.dy = 0

    def jump(self):
        if self.on_ground:
            self.dy = self.jump_speed

    @property
    def _local_vertical(self):
        return np.array([
            (-0.2, -0.2, -0.2),  # 0
            (+0.2, -0.2, -0.2),  # 1
            (+0.2, +0.2, -0.2),  # 2
            (-0.2, +0.2, -0.2),  # 3
            (-0.2, -0.2, +0.2),  # 4
            (+0.2, -0.2, +0.2),  # 5
            (+0.2, +0.2, +0.2),  # 6
            (-0.2, +0.2, +0.2),  # 7
        ])

    @property
    def verticals(self):
        return self._local_vertical + math3.rotation_matrix(self.yaw, self.pitch) @ self.rect.pos
    
    @property
    def faces(self):
        return [
            [(4, 5, 6, 7), "back"],  # +Z
            [(0, 1, 2, 3), "front"],  # -Z
            [(1, 5, 6, 2), "right"],  # +X
            [(0, 4, 7, 3), "left"],  # -X
            [(3, 2, 6, 7), "top"],  # +Y (윗면)
            [(0, 1, 5, 4), "bottom"]  # -Y (아랫면)
        ]