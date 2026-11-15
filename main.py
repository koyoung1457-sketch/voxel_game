import pygame, sys
from pygame.locals import DOUBLEBUF, OPENGL

import raycast
import texture
from player import Player
from world import World
from rendering import Rendering
from rect3 import *
import entity as Entity
from UI import UI

WIDTH, HEIGHT = 1000, 1000

pygame.init()
pygame.display.set_caption('원근 투영 (OpenGL)')

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# 기존에는 pygame.display.set_mode((1000, 1000)) 만으로 2D 서피스를 만들고
# 거기에 픽셀을 직접 찍었지만, OpenGL을 쓰려면 DOUBLEBUF | OPENGL 플래그로
# OpenGL 렌더링 컨텍스트가 붙은 창을 만들어야 합니다.
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)

# OpenGL 컨텍스트(창)가 생긴 '뒤에' 텍스처를 불러와야 합니다.
texture.load_all_textures()

player = Player()
world = World()
entities = []
render = Rendering(WIDTH, HEIGHT)
render.set_projection(player.camera.fov)
ui = UI(WIDTH, HEIGHT)

clock = pygame.time.Clock()

for i in range(5):
    for j in range(5):
        world.add((i - 2, 0, j - 2), 'dirt')
        world.add((i - 2, 0, j - 2), 'dirt')
        world.add((i - 2, 0, j - 2), 'dirt')

player.spawn(world, keep_inventory= True)

while 1:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_RETURN:
                print(player.x, player.y, player.z)
        # 마우스 클릭 이벤트
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 레이캐스트 발사! (최대 거리 10칸 설정)
            hit, place = raycast.raycast(player.cx, player.cy, player.cz, player.camera.yaw, player.camera.pitch, world, max_dist=10.0)

            if hit is not None:
                if event.button == 1:  # 마우스 왼쪽 클릭: 파괴
                    entities.append(Entity.Block(hit[0], hit[1], hit[2], 0, 0, 0, world.get_kind(hit)))
                    world.remove(hit)

                elif event.button == 3:  # 마우스 오른쪽 클릭: 설치
                    if not world.has(place):
                        if player.inventory[player.inventory_idx].kind is not None:
                            world.add(place, player.now_block)
                            if player.rect.colliderect(block_rect(place)):
                                world.remove(place)
                            else:
                                player.discount()

    key = pygame.key.get_pressed()

    player.move(key, screen)
    player.update(world, dt)

    for entity in entities:
        entity.update(world, dt)
        if (entity.x-player.x)**2+(entity.y-player.y)**2+(entity.z-player.z)**2 < 1:
            has = player.has_item(entity.kind)
            ntt_kill = player.get_item(entity.kind, has)
            if ntt_kill:
                entities.remove(entity)

            continue
        if entity.y  <-50:
            entities.remove(entity)
            continue

    if player.y < -50:
        player.spawn(world, keep_inventory=True)

    # 지금 보고 있는 블록을 매 프레임 찾아서 테두리(와이어프레임)로 표시합니다.
    hover_hit, _ = raycast.raycast(player.cx, player.cy, player.cz, player.camera.yaw, player.camera.pitch, world, max_dist=10.0)

    render.begin_frame()
    render.painters_algorithm(player.cx, player.cy, player.cz, player.camera.yaw, player.camera.pitch, world, entities)

    if hover_hit is not None:
        render.draw_block_wireframe(player.cx, player.cy, player.cz, player.camera.yaw, player.camera.pitch, hover_hit)


    ui.update()
    render.draw_surface(ui.draw(player.inventory, player.inventory_idx, player.hp))

    pygame.display.flip()