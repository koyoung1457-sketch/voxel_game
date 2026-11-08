import math, pygame
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

import math3
import texture

# 텍스처가 전혀 준비되지 않은 극단적인 경우(예: load_all_textures()를 아직 호출하지
# 않은 상태)에만 쓰는 고정 폴백 색입니다. 정상적으로는 texture.get_texture()가
# 항상 유효한 텍스처(정상 텍스처 또는 누락 텍스처)를 돌려주므로 거의 쓰일 일이 없습니다.
FALLBACK_COLOR = (255, 0, 255)

# (x오프셋, y오프셋, z오프셋), 정점 인덱스, 텍스처 면 이름
FACE_DEFS = (
    ((0, 0, 1), (4, 5, 6, 7), "side"),    # +Z
    ((0, 0, -1), (0, 1, 2, 3), "side"),   # -Z
    ((1, 0, 0), (1, 5, 6, 2), "side"),    # +X
    ((-1, 0, 0), (0, 4, 7, 3), "side"),   # -X
    ((0, 1, 0), (3, 2, 6, 7), "top"),     # +Y (윗면)
    ((0, -1, 0), (0, 1, 5, 4), "bottom"), # -Y (아랫면)
)

# 정점 4개 순서에 맞춘 UV 좌표 (좌하단 -> 우하단 -> 우상단 -> 좌상단)
FACE_UV = ((0, 0), (1, 0), (1, 1), (0, 1))

# 와이어프레임 큐브의 모서리 12개 (정점 인덱스 쌍)
CUBE_EDGES = (
    (0, 1), (1, 2), (2, 3), (3, 0),  # 뒷면
    (4, 5), (5, 6), (6, 7), (7, 4),  # 앞면
    (0, 4), (1, 5), (2, 6), (3, 7),  # 앞뒤 연결
)


class Rendering:
    """
    카메라 회전/이동 수식(math3.world_to_screen)은 기존 그대로 재사용하고,
    "투영 + 폴리곤 채우기 + 깊이 정렬 + 텍스처 입히기"를 OpenGL(GPU)에게 맡깁니다.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

        glEnable(GL_DEPTH_TEST)
        glClearColor(94 / 255, 194 / 255, 209 / 255, 1.0)

    def set_projection(self, fov, near=0.05, far=200.0):
        # 기존 math3.project()는 "가로" 화면 기준 focal length를 썼으므로
        # (수평 FOV 기준), gluPerspective가 요구하는 수직 FOV로 변환해줍니다.
        aspect = self.width / self.height
        horizontal_fov_rad = math.radians(fov)
        vertical_fov_rad = 2 * math.atan(math.tan(horizontal_fov_rad / 2) / aspect)
        vertical_fov_deg = math.degrees(vertical_fov_rad)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(vertical_fov_deg, aspect, near, far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def begin_frame(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def painters_algorithm(self, cx, cy, cz, yaw, pitch, world, entities):
        # 이름은 기존 코드와 맞춰뒀지만, 실제 앞/뒤 정렬은
        # glEnable(GL_DEPTH_TEST)로 GPU의 Z-buffer가 처리합니다.
        for x, y, z in world.blocks:
            kind = world.blocks2[(x, y, z)]

            for (dx, dy, dz), idx, face_name in FACE_DEFS:
                if world.has((x + dx, y + dy, z + dz)):
                    continue  # 이웃 블록에 가려진 면은 그리지 않음

                tex_id = texture.get_texture(kind, face_name)
                self._draw_face(cx, cy, cz, yaw, pitch, x, y, z, idx, tex_id)

        for entity in entities:
            for face, face_name in entity.faces:
                tex_id = texture.get_texture(entity.kind, face_name, entity=True)
                self._draw_entity_face(cx, cy, cz, yaw, pitch, face, entity.verticals, tex_id)

    def _draw_entity_face(self, cx, cy, cz, yaw, pitch, face, verticals, tex_id):
        if tex_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glColor3f(1.0, 1.0, 1.0)  # 텍스처 원래 색 그대로 나오게
        else:
            glDisable(GL_TEXTURE_2D)
            r, g, b = FALLBACK_COLOR
            glColor3f(r / 255, g / 255, b / 255)

        glBegin(GL_QUADS)
        for (u, vv), i in zip(FACE_UV, face):
            vx, vy, vz = verticals[i]
            cxs, cys, czs = math3.world_to_screen(cx, cy, cz,  vx, vy, vz, yaw, pitch)

            if tex_id is not None:
                glTexCoord2f(u, vv)

            glVertex3f(cxs, cys, -czs)
        glEnd()

    def _draw_face(self, cx, cy, cz, yaw, pitch, x, y, z, idx, tex_id):
        v = [
            (x - 0.5, y - 0.5, z - 0.5),  # 0
            (x + 0.5, y - 0.5, z - 0.5),  # 1
            (x + 0.5, y + 0.5, z - 0.5),  # 2
            (x - 0.5, y + 0.5, z - 0.5),  # 3
            (x - 0.5, y - 0.5, z + 0.5),  # 4
            (x + 0.5, y - 0.5, z + 0.5),  # 5
            (x + 0.5, y + 0.5, z + 0.5),  # 6
            (x - 0.5, y + 0.5, z + 0.5),  # 7
        ]

        if tex_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glColor3f(1.0, 1.0, 1.0)  # 텍스처 원래 색 그대로 나오게
        else:
            glDisable(GL_TEXTURE_2D)
            r, g, b = FALLBACK_COLOR
            glColor3f(r / 255, g / 255, b / 255)

        glBegin(GL_QUADS)
        for (u, vv), i in zip(FACE_UV, idx):
            vx, vy, vz = v[i]
            cxs, cys, czs = math3.world_to_screen(cx, cy, cz, vx, vy, vz, yaw, pitch)

            if tex_id is not None:
                glTexCoord2f(u, vv)

            # math3의 카메라 좌표계는 "카메라 앞 = +z" 인데
            # OpenGL 기본 카메라는 "카메라 앞 = -z" 이므로 z 부호만 뒤집어줍니다.
            glVertex3f(cxs, cys, -czs)
        glEnd()

    def draw_block_wireframe(self, cx, cy, cz, yaw, pitch, block_pos, color=(0, 0, 0)):
        """block_pos(그 블록의 (x, y, z))에 검은 테두리 큐브를 그려서
        '지금 보고 있는 블록'을 표시합니다. raycast.py의 hit 결과를 그대로 넣어주면 됩니다."""
        x, y, z = block_pos
        # 블록 표면(0.5)보다 살짝 크게(0.501) 그려야 선이 표면과 딱 겹쳐서
        # 깜빡이는 현상(Z-fighting)이 생기지 않습니다.
        s = 0.501
        v = [
            (x - s, y - s, z - s),  # 0
            (x + s, y - s, z - s),  # 1
            (x + s, y + s, z - s),  # 2
            (x - s, y + s, z - s),  # 3
            (x - s, y - s, z + s),  # 4
            (x + s, y - s, z + s),  # 5
            (x + s, y + s, z + s),  # 6
            (x - s, y + s, z + s),  # 7
        ]

        glDisable(GL_TEXTURE_2D)
        r, g, b = color
        glColor3f(r / 255, g / 255, b / 255)
        glLineWidth(2.0)

        glBegin(GL_LINES)
        for a, b_idx in CUBE_EDGES:
            for i in (a, b_idx):
                vx, vy, vz = v[i]
                cxs, cys, czs = math3.world_to_screen(cx, cy, cz, vx, vy, vz, yaw, pitch)
                glVertex3f(cxs, cys, -czs)
        glEnd()

    def draw_crosshair(self):
        # 3D 장면 위에 2D 십자선을 그리기 위해 잠깐 직교 투영으로 전환합니다.
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        glVertex2f(self.width / 2 - 10, self.height / 2)
        glVertex2f(self.width / 2 + 10, self.height / 2)
        glVertex2f(self.width / 2, self.height / 2 - 10)
        glVertex2f(self.width / 2, self.height / 2 + 10)
        glEnd()
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_surface(self, surface):
        # Surface를 OpenGL 텍스처로 변환
        width, height = surface.get_size()
        image_data = pygame.image.tostring(surface, "RGBA", True)

        # UI 텍스처를 임시로 생성
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            width, height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image_data
        )

        # 2D 좌표계로 전환
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 투명도 적용
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)

        glColor4f(1, 1, 1, 1)

        # 화면 전체에 UI 출력
        glBegin(GL_QUADS)

        glTexCoord2f(0, 1)
        glVertex2f(0, 0)

        glTexCoord2f(1, 1)
        glVertex2f(width, 0)

        glTexCoord2f(1, 0)
        glVertex2f(width, height)

        glTexCoord2f(0, 0)
        glVertex2f(0, height)

        glEnd()

        # OpenGL 상태 복구
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)

        # 임시 텍스처 삭제
        glDeleteTextures([tex_id])