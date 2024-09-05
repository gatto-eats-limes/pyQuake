import numpy as np
from math import sin, cos, radians

# Fun
class Player:
    def __init__(self, position, up_vector):
        self.position = np.array(position, dtype='f4')
        self.up_vector = np.array(up_vector, dtype='f4')
        self.yaw = -90.0
        self.pitch = 0.0
        self.front = np.array([0.0, 0.0, -1.0], dtype='f4')
        self.speed = 5.0  # Adjust speed as needed
        self.jump_force = 2.8
        self.grounded = True
        self.gravity = -9.81
        self.velocity = np.array([0.0, 0.0, 0.0], dtype='f4')
        self.friction = 0.1
        self.acceleration = 10.0  # Acceleration value

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

    def jump(self):
        if self.grounded:
            self.velocity[1] = self.jump_force
            self.grounded = False

    def apply_gravity(self, delta_time):
        if not self.grounded:
            self.velocity[1] += self.gravity * delta_time
            self.position[1] += self.velocity[1] * delta_time

        if self.position[1] <= 0:  # Assuming ground is at y = 0
            self.position[1] = 0
            self.grounded = True
            self.velocity[1] = 0

    def update_velocity(self, forward_input, right_input, delta_time):
        # Calculate acceleration based on input
        forward_acceleration = self.acceleration * forward_input
        right_acceleration = self.acceleration * right_input

        # Update velocity based on acceleration
        self.velocity[0] += right_acceleration * self.right[0] * delta_time
        self.velocity[0] += forward_acceleration * self.front[0] * delta_time
        self.velocity[2] += right_acceleration * self.right[2] * delta_time
        self.velocity[2] += forward_acceleration * self.front[2] * delta_time

        # Apply friction
        self.velocity[0] *= (1.0 - self.friction)
        self.velocity[2] *= (1.0 - self.friction)

        # Update position based on velocity
        self.position += self.velocity * delta_time

    def check_collision(self, min_bound, max_bound):
        player_min = np.array([self.position[0] - 0.25, self.position[1] - 0.5, self.position[2] - 0.25])
        player_max = np.array([self.position[0] + 0.25, self.position[1] + 0.5, self.position[2] + 0.25])

        if (player_min[0] < max_bound[0] and player_max[0] > min_bound[0] and
            player_min[1] < max_bound[1] and player_max[1] > min_bound[1] and
            player_min[2] < max_bound[2] and player_max[2] > min_bound[2]):
            return True
        return False

    def resolve_collision(self, min_bound, max_bound):
        player_min = np.array([self.position[0] - 0.25, self.position[1] - 0.5, self.position[2] - 0.25])
        player_max = np.array([self.position[0] + 0.25, self.position[1] + 0.5, self.position[2] + 0.25])

        overlap_x = min(max_bound[0] - player_min[0], player_max[0] - min_bound[0])
        overlap_y = min(max_bound[1] - player_min[1], player_max[1] - min_bound[1])
        overlap_z = min(max_bound[2] - player_min[2], player_max[2] - min_bound[2])

        if overlap_x < overlap_y and overlap_x < overlap_z:
            if self.position[0] < (min_bound[0] + max_bound[0]) / 2:
                self.position[0] -= overlap_x  # Push player left
            else:
                self.position[0] += overlap_x  # Push player right
        elif overlap_y < overlap_x and overlap_y < overlap_z:
            if self.position[1] < (min_bound[1] + max_bound[1]) / 2:
                self.position[1] -= overlap_y  # Push player down
            else:
                self.position[1] += overlap_y  # Push player up
        else:
            if self.position[2] < (min_bound[2] + max_bound[2]) / 2:
                self.position[2] -= overlap_z  # Push player back
            else:
                self.position[2] += overlap_z  # Push player forward
