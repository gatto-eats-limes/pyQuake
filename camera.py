# camera.py

import numpy as np
from math import sin, cos, radians

class Camera:
    def __init__(self, position, up_vector):
        self.position = np.array(position, dtype='f4')
        self.up_vector = np.array(up_vector, dtype='f4')
        self.yaw = -90.0
        self.pitch = 0.0
        self.front = np.array([0.0, 0.0, -1.0], dtype='f4')
        self.update_camera_vectors()

    def update_camera_vectors(self):
        front = np.array([
            cos(radians(self.yaw)) * cos(radians(self.pitch)),
            sin(radians(self.pitch)),
            sin(radians(self.yaw)) * cos(radians(self.pitch))
        ], dtype='f4')
        self.front = front / np.linalg.norm(front)
        self.right = np.cross(self.front, self.up_vector)
        self.right /= np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)
        self.up /= np.linalg.norm(self.up)

    def create_view_matrix(self):
        return np.array([
            [self.right[0], self.up[0], -self.front[0], 0.0],
            [self.right[1], self.up[1], -self.front[1], 0.0],
            [self.right[2], self.up[2], -self.front[2], 0.0],
            [-np.dot(self.right, self.position), -np.dot(self.up, self.position), np.dot(self.front, self.position), 1.0]
        ], dtype='f4')

    def process_mouse_movement(self, x_offset, y_offset, sensitivity=0.1):
        self.yaw += x_offset * sensitivity
        self.pitch -= y_offset * sensitivity
        self.update_camera_vectors()

    def strafe(self, direction, amount):
        self.position += direction * self.right * amount

    def move_forward(self, amount):
        self.position += self.front * amount
