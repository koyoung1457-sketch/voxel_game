import math3
import numpy as np

class LocalPos:
    def __init__(self, pos):
        self.pos = pos

    def world_pos(self, o, yaw, pitch):
        p = math3.rotation_matrix(yaw, pitch)

        return p @ self.pos + o