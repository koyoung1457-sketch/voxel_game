import pygame, sys

pygame.init()
pygame.display.set_caption("draw triangle without pygame.draw.polygon()")
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

x1, y1 = None, None
x2, y2 = None, None
x3, y3 = None, None

dot_idx = 0

def barycentric(x, y, ax, ay, bx, by, cx, cy):
    den = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)

    alpha = ((by-cy)*(x-cx) + (cx-bx)*(y-cy)) / den
    beta  = ((cy-ay)*(x-cx) + (ax-cx)*(y-cy)) / den
    gamma = 1 - alpha - beta

    return alpha, beta, gamma

def draw_polygon(screen, x1, y1, x2, y2, x3, y3, c1, c2, c3):
    xmin = max(0, int(min(x1, x2, x3)))
    xmax = min(screen.get_width() - 1, int(max(x1, x2, x3)))

    ymin = max(0, int(min(y1, y2, y3)))
    ymax = min(screen.get_height() - 1, int(max(y1, y2, y3)))

    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            alpha, beta, gamma = barycentric(x, y, x1, y1, x2, y2, x3, y3)
            if alpha >= 0 and beta >= 0 and gamma >= 0:
                r = alpha*c1[0] + beta*c2[0] + gamma*c3[0]
                g = alpha*c1[1] + beta*c2[1] + gamma*c3[1]
                b = alpha*c1[2] + beta*c2[2] + gamma*c3[2]
                screen.set_at((x, y), (int(r), int(g), int(b)))

while 1:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if dot_idx == 0:
                x1, y1 = pygame.mouse.get_pos()

            if dot_idx == 1:
                x2, y2 = pygame.mouse.get_pos()

            if dot_idx == 2:
                x3, y3 = pygame.mouse.get_pos()

            dot_idx = (dot_idx + 1) % 4

    if dot_idx >= 1:
        screen.set_at((x1, y1), (255, 0, 0))

    if dot_idx >= 2:
        screen.set_at((x2, y2), (0, 255, 0))

    if dot_idx >= 3:
        screen.set_at((x3, y3), (0, 0, 255))
        draw_polygon(screen, x1, y1, x2, y2, x3, y3, (255, 0, 0), (0, 255, 0), (0, 0, 255))

    pygame.display.update()