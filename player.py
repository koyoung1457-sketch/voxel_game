import pygame
import math
from camera import Camera
from rect3 import *
import entity

class Player:
    def __init__(self, spawn_pos = (0, 0, 0)):
        self.rect = EntityRect(spawn_pos[0], spawn_pos[1], spawn_pos[2], 0.6, 1.9, 0.6)
        self.speed = 5

        self.vx = 0
        self.vy = 0
        self.vz = 0

        self.jump_speed = 8
        self.on_ground = False

        self.camera = Camera()

        self.inventory = [
            entity.Item('dirt', 5),
            entity.Item('grass', 5),
            entity.Item('stone', 5),
            entity.Item('oak_log', 5),
            entity.Item(None, 0),
            entity.Item(None, 0),
            entity.Item(None, 0),
            entity.Item(None, 0),
            entity.Item(None, 0),
            ]
        self.inventory_idx = 0

        self.spawn_pos = spawn_pos

        self.hp = 20

        self.highest_y = -float("inf")
        self.past_on_ground = False
        self.damage_height = 3
    def move(self, key, screen):
        dx, dz = 0, 0

        self.vx = 0
        self.vz = 0

        if key[pygame.K_w]:
            dx += math.sin(self.camera.yaw)
            dz += math.cos(self.camera.yaw)

        if key[pygame.K_s]:
            dx -= math.sin(self.camera.yaw)
            dz -= math.cos(self.camera.yaw)

        if key[pygame.K_a]:
            dx -= math.cos(self.camera.yaw)
            dz += math.sin(self.camera.yaw)

        if key[pygame.K_d]:
            dx += math.cos(self.camera.yaw)
            dz -= math.sin(self.camera.yaw)

        l = math.hypot(dx, dz)
        if l:
            dx /= l
            dz /= l

        self.vx = dx * self.speed
        self.vz = dz * self.speed

        if key[pygame.K_SPACE]:
            if self.on_ground:
                self.vy = self.jump_speed

        mx, my = pygame.mouse.get_pos()

        mx -= screen.get_width() // 2
        my -= screen.get_height() // 2

        pygame.mouse.set_pos((screen.get_width() // 2, screen.get_height() // 2))

        self.camera.yaw += mx * self.camera.sensitive
        self.camera.pitch -= my * self.camera.sensitive
        self.camera.pitch = max(-math.pi / 2 + 0.01,
                      min(math.pi / 2 - 0.01, self.camera.pitch))

        if key[pygame.K_1]:
            self.inventory_idx = 0

        if key[pygame.K_2]:
            self.inventory_idx = 1

        if key[pygame.K_3]:
            self.inventory_idx = 2

        if key[pygame.K_4]:
            self.inventory_idx = 3

        if key[pygame.K_5]:
            self.inventory_idx = 4

        if key[pygame.K_6]:
            self.inventory_idx = 5

        if key[pygame.K_7]:
            self.inventory_idx = 6

        if key[pygame.K_8]:
            self.inventory_idx = 7

        if key[pygame.K_9]:
            self.inventory_idx = 8

    def update(self, world, dt, gravity):
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
            self.vy -= gravity * dt

            self.rect.y += self.vy * dt

            self.past_on_ground = self.on_ground

            self.on_ground = False

            for block in blocks:
                rect = block_rect(block)
                if self.rect.colliderect(rect):

                    if self.vy < 0:
                        self.rect.y = rect.top
                        self.vy = 0
                        self.on_ground = True
                        if not self.past_on_ground:
                            if self.y + self.damage_height < self.highest_y:
                                self.hp -= self.highest_y - self.y - self.damage_height

                    elif self.vy > 0:
                        self.rect.y = rect.bottom - self.rect.height
                        self.vy = 0

    def _collides(self, world, x, y, z):
        test = EntityRect(
            x, y, z,
            self.rect.width,
            self.rect.height,
            self.rect.depth
        )

        for block in world.blocks:
            if test.colliderect(block_rect(block)):
                return True

        return False

    def _has_ground(self, world, x, y, z):
        feet = EntityRect(
            x, y - 0.05, z,
            self.rect.width, 0.1, self.rect.depth
        )

        for block in world.blocks:
            if feet.colliderect(block_rect(block)):
                return True

        return False

    def find_free_spawn(self, world, radius=8, step=0.5):
        """spawn_pos에서 가장 가까운, 블록과 겹치지 않는 위치를 찾는다"""
        sx, sy, sz = self.spawn_pos
        n = int(radius / step)
        offsets = [
            (i * step, j * step, k * step)
            for i in range(-n, n + 1)
            for j in range(-n, n + 1)
            for k in range(-n, n + 1)
        ]
        # 가까운 순, 거리가 같으면 위쪽 우선
        offsets.sort(key=lambda o: (o[0] ** 2 + o[1] ** 2 + o[2] ** 2, -o[1]))

        for ox, oy, oz in offsets:
            if (
                    not self._collides(world, sx + ox, sy + oy, sz + oz)
                    and self._has_ground(world, sx + ox, sy + oy, sz + oz)
            ):
                return sx + ox, sy + oy, sz + oz

        print("주변에서 빈 공간을 찾지 못함!")
        return self.spawn_pos  # 반경 안에 빈 곳이 없으면 그냥 원래 위치

    def spawn(self, world, keep_inventory=False):
        self.rect.pos = self.find_free_spawn(world)
        self.vx = self.vy = self.vz = 0
        if not keep_inventory:
            self.inventory = [entity.Item(None, 0)] * 9
    @property
    def now_block(self):
        return self.inventory[self.inventory_idx].kind

    def discount(self):
        if self.inventory[self.inventory_idx].kind is not None:
            self.inventory[self.inventory_idx].discount(1)

    def has_item(self, kind):
        for i in range(9):
            if self.inventory[i].kind == kind:
                return i
        return None

    def get_item(self, kind, idx):
        if idx is not None:
            self.inventory[idx].count += 1
            return True
        else:
            for i in range(9):
                if self.inventory[i].kind is None:
                    self.inventory[i].kind = kind
                    self.inventory[i].count += 1
                    return True
            return False

    @property
    def cx(self):
        return self.x

    @property
    def cy(self):
        return 1.4 + self.y

    @property
    def cz(self):
        return self.z

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def z(self):
        return self.rect.z

    @property
    def pos(self):
        return np.array([self.x, self.y, self.z])