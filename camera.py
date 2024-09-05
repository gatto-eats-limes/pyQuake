import numpy as np
from math import sin, cos, radians

class Camera:
    def __init__(self, position, up_vector):
        self.position = np.array(position, dtype='f4')
        self.up_vector = np.array(up_vector, dtype='f4')
        self.yaw = -90.0
        self.pitch = 0.0
        self.front = np.array([0.0, 0.0, -1.0], dtype='f4')
        self.speed = 34.0  # Speed of the player
        self.jump_force = 2.8
        self.grounded = True  # Is the player grounded?
        self.gravity = -9.81  # Gravity value
        self.velocity = np.array([0.0, 0.0, 0.0], dtype='f4')  # Initial velocity
        self.friction = 0.18  # Friction coefficient

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
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        self.update_camera_vectors()

    def strafe(self, direction, delta_time):
        velocity = self.speed * delta_time
        self.position += direction * self.right * velocity

    def move_forward(self, direction, delta_time):
        velocity = self.speed * delta_time
        forward_flat = np.array([self.front[0], 0, self.front[2]])
        forward_flat /= np.linalg.norm(forward_flat)  # Normalize the flat forward vector
        self.position += direction * forward_flat * velocity

    def jump(self):
        if self.grounded:
            self.velocity[1] = self.jump_force
            self.grounded = False

    def apply_gravity(self, delta_time):
        if not self.grounded:
            self.velocity[1] += self.gravity * delta_time
            self.position[1] += self.velocity[1] * delta_time

        # Check if on ground
        if self.position[1] <= 0:  # Assuming ground is at y = 0
            self.position[1] = 0
            self.grounded = True
            self.velocity[1] = 0

    def update_velocity(self, forward_input, right_input, delta_time):
        # Apply input to velocity
        if forward_input != 0:
            forward_velocity = self.speed * forward_input * delta_time
            self.velocity[0] += forward_velocity * self.front[0]
            self.velocity[2] += forward_velocity * self.front[2]

        if right_input != 0:
            right_velocity = self.speed * right_input * delta_time
            self.velocity[0] += right_velocity * self.right[0]
            self.velocity[2] += right_velocity * self.right[2]

        # Apply friction
        self.velocity[0] *= (1.0 - self.friction)
        self.velocity[2] *= (1.0 - self.friction)

        # Update position based on velocity
        self.position += self.velocity * delta_time