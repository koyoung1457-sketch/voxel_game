import math

def project(x, y, z, fov, width, height):
    if z <= 0:
        return None, None

    focal = width / (2 * math.tan(math.radians(fov) / 2))

    screen_x = width / 2 + x * focal / z
    screen_y = height / 2 - y * focal / z

    return screen_x, screen_y

def world_to_screen(cx, cy, cz, x,  y, z, yaw, pitch):
    x -= cx
    y -= cy
    z -= cz

    nx = x * math.cos(yaw) - z * math.sin(yaw)
    nz = x * math.sin(yaw) + z * math.cos(yaw)
    x, z = nx, nz

    ny = y*math.cos(pitch) - z*math.sin(pitch)
    nz = y*math.sin(pitch) + z*math.cos(pitch)
    y, z = ny, nz

    return x, y, z

def barycentric(x, y, ax, ay, bx, by, cx, cy):
    den = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)

    alpha = ((by-cy)*(x-cx) + (cx-bx)*(y-cy)) / den
    beta  = ((cy-ay)*(x-cx) + (ax-cx)*(y-cy)) / den
    gamma = 1 - alpha - beta

    return alpha, beta, gamma