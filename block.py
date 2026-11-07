from rect3 import BlockRect
import texture

class Block:
    def __init__(self, pos, kind):
        self.rect = BlockRect(pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5, 1, 1, 1)
        # kind: 블록 종류 문자열 (예: "dirt", "grass", "stone")
        # blocks.BLOCK_TEXTURES에서 이 값으로 텍스처를 찾습니다.
        self.kind = kind

    def get_texture(self, face):
        return texture.get_texture(self.kind, face)