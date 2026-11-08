import pygame

class UI:
    def __init__(self, width, height):
        self.surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

    def update(self):
        pass

    def draw(self, inventory, inventory_idx, hp):
        self.surface.fill((0, 0, 0, 0))

        # 십자선
        cx = self.width // 2
        cy = self.height // 2

        pygame.draw.line(
            self.surface, (0, 0, 0),
            (cx - 10, cy), (cx + 10, cy), 2
        )

        pygame.draw.line(
            self.surface, (0, 0, 0),
            (cx, cy - 10), (cx, cy + 10), 2
        )

        for i in range(9):
            pygame.draw.rect(
                self.surface,
                (255, 255, 255),
                (self.width * (2 * i + 1) / 20, self.height * 17 / 20,
                 self.width * 1 / 10, self.height / 10),
                5
            )

        pygame.draw.rect(
            self.surface,
            (127, 127, 127),
            (self.width * (2 * inventory_idx + 1) / 20, self.height * 17 / 20,
             self.width * 1 / 10, self.height / 10),
            10
        )

        return self.surface

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()