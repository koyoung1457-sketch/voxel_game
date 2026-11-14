import os
import pygame
from OpenGL.GL import (
    glGenTextures, glBindTexture, glTexParameteri, glTexImage2D,
    GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_NEAREST, GL_REPEAT,
    GL_RGBA, GL_UNSIGNED_BYTE,
)

import blocks

# 텍스처 파일이 없는 블록/면에 대신 씌울 "누락 텍스처" 이미지 경로.
# 이 경로에 파일을 직접 만들어 두면 그 이미지가 쓰이고,
# 없으면 아래 _generate_missing_surface()가 자동으로 체크무늬를 그려서 대신 씁니다.
DEFAULT_TEXTURE_PATH = "textures/missing.png"

# (kind, face) -> OpenGL 텍스처 id
# face는 "top" / "bottom" / "side" / "all" 중 하나입니다.
_texture_block_cache = {}
_texture_entity_cache = {}
_item_cache = {}

# 누락 텍스처(위 DEFAULT_TEXTURE_PATH 또는 자동 생성 체크무늬)의 텍스처 id.
# load_all_textures()가 호출되기 전까지는 None입니다.
_default_texture_id = None


def _generate_missing_surface(size=16):
    """missing.png가 없을 때 자동으로 만드는 보라/검정 체크무늬 (흔히 쓰는 '텍스처 없음' 표시)."""
    surface = pygame.Surface((size, size))
    half = size // 2
    surface.fill((0, 0, 0))
    pygame.draw.rect(surface, (255, 0, 255), (0, 0, half, half))
    pygame.draw.rect(surface, (255, 0, 255), (half, half, half, half))
    return surface.convert_alpha()


def _surface_to_gl_texture(surface):
    """pygame Surface 하나를 OpenGL 텍스처로 등록하고 텍스처 id를 돌려줍니다."""
    # OpenGL 텍스처 좌표는 아래에서 위로 증가하는데 pygame 이미지는 위에서 아래로
    # 저장되어 있어서, 세로로 한 번 뒤집어줘야 텍스처가 거꾸로 나오지 않습니다.
    surface = pygame.transform.flip(surface, False, True)

    width, height = surface.get_size()
    # 위에서 이미 뒤집었으므로 tostring은 flipped=False(기본값)로 둡니다.
    image_data = pygame.image.tostring(surface, "RGBA")

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, image_data,
    )

    return tex_id


def _load_gl_texture(path):
    """이미지 파일 경로를 읽어서 OpenGL 텍스처로 등록합니다."""
    surface = pygame.image.load(path).convert_alpha()
    return _surface_to_gl_texture(surface)

def _load_pg_texture(path, size=(80, 80)):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

def _load_default_texture():
    global _default_texture_id

    if os.path.exists(DEFAULT_TEXTURE_PATH):
        surface = pygame.image.load(DEFAULT_TEXTURE_PATH).convert_alpha()
    else:
        surface = _generate_missing_surface()

    _default_texture_id = _surface_to_gl_texture(surface)


def load_all_textures():
    """
    blocks.BLOCK_TEXTURES에 적힌 모든 종류(kind)의 텍스처를 미리 읽어들이고,
    누락 텍스처(기본/대체 이미지)도 함께 준비합니다.
    반드시 pygame 창(OpenGL 컨텍스트)이 만들어진 '뒤에' 한 번만 호출하세요.

    특정 종류/면의 이미지 파일이 실제로 없으면 조용히 건너뛰고,
    나중에 get_texture()가 대신 누락 텍스처 id를 돌려줍니다.
    """
    _load_default_texture()

    for kind, faces in blocks.BLOCK_TEXTURES.items():
        for face_key, path in faces.items():
            if not os.path.exists(path):
                print(f"[texture] 이미지가 없어서 누락 텍스처로 대체합니다: {kind}/{face_key} -> {path}")
                continue

            _texture_block_cache[(kind, face_key)] = _load_gl_texture(path)
    for kind, faces in blocks.ENTITY_TEXTURES.items():
        for face_key, path in faces.items():
            if not os.path.exists(path):
                print(f"[texture] 이미지가 없어서 누락 텍스처로 대체합니다: {kind}/{face_key} -> {path}")
                continue

            _texture_entity_cache[(kind, face_key)] = _load_gl_texture(path)
    for kind, path in blocks.ITEM_TEXTURE.items():
        if not os.path.exists(path):
            print(f"[texture] 아이템 이미지가 없어서 누락 텍스처로 대체합니다: {kind} -> {path}")
            continue
        _item_cache[kind] = _load_pg_texture(path)


def get_texture(kind, face, entity=False):
    """
    kind: 블록 종류 문자열 (Block.kind / world.blocks2에 들어있는 값과 동일)
    face: "top" | "bottom" | "side"

    해당 종류/면에 등록된 텍스처 id를 돌려줍니다.
    - 직접 그 면에 대한 이미지가 등록돼 있으면 그걸 씁니다.
    - "all" 하나만 등록된 블록은 top/bottom/side 어떤 걸 물어봐도 그 텍스처를 씁니다.
    - 둘 다 없으면(파일이 없거나 아예 BLOCK_TEXTURES에 정의 안 된 종류) 단색 대신
      DEFAULT_TEXTURE_PATH(또는 자동 생성된 체크무늬) 텍스처 id를 돌려줍니다.
    """
    if not entity:
        if (kind, face) in _texture_block_cache:
            return _texture_block_cache[(kind, face)]

        if (kind, "all") in _texture_block_cache:
            return _texture_block_cache[(kind, "all")]

        return _default_texture_id
    else:
        if (kind, face) in _texture_entity_cache:
            return _texture_entity_cache[(kind, face)]

        if (kind, "all") in _texture_entity_cache:
            return _texture_entity_cache[(kind, "all")]

        return _default_texture_id

def get_item_texture(kind):
    return _item_cache[kind]