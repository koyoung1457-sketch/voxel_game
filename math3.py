import math
import numpy as np

def look_at(origin, target):
    d = target - origin
    dx, dy, dz = d
    yaw = math.atan2(dx, dz)
    pitch = math.atan2(dy, math.hypot(dx, dz))

    return yaw, pitch

def rotation_matrix(yaw, pitch):
    y, p = yaw, pitch
    ry = np.array([
        [np.cos(y), 0, -np.sin(y)],
        [0, 1, 0],
        [np.sin(y), 0, np.cos(y)]
    ])
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(p), -np.sin(p)],
        [0, np.sin(p), np.cos(p)]
    ])

    return rx @ ry
def project(x, y, z, fov, width, height):
    if z <= 0:
        return None, None

    focal = width / (2 * math.tan(math.radians(fov) / 2))

    screen_x = width / 2 + x * focal / z
    screen_y = height / 2 - y * focal / z

    return screen_x, screen_y

def world_to_screen(cx, cy, cz, x,  y, z, yaw, pitch):
    pos = np.array([x-cx, y-cy, z-cz])

    R = rotation_matrix(yaw, pitch)
    pos = R @ pos

    return tuple(pos)