import numpy as np
from math import sin, cos, radians, pi

class Player:
    def __init__(self, position, up_vector):
        self.position = np.array(position, dtype='f4')
        self.up_vector = np.array(up_vector, dtype='f4')
        self.yaw = -90.0  # Looking straight forward
        self.pitch = 0.0  # Level pitch
        self.front = np.array([0.0, 0.0, -1.0], dtype='f4')  # Initial forward direction

        # Player movement attributes
        self.speed = 36.0  # Increased movement speed
        self.jump_force = 5.0  # Higher jump force for more vertical mobility
        self.grounded = False
        self.gravity = -12.0 # Increased gravity for faster falling
        self.velocity = np.array([0.0, 0.0, 0.0], dtype='f4')
        self.friction = 0.3  # Lower friction for more slide
        self.acceleration = 48.0  # Increased acceleration for quicker movement responsiveness

        # Player size attributes
        self.width = 0.6  # Width of the player for collision detection
        self.height = 1.2  # Height of the player for collision detection
        self.length = 0.6  # Length of the player for collision detection

        # Camera bobbing attributes
        self.bob_amplitude = 0.025  # Reduced amplitude of bobbing effect
        self.bob_frequency = 3.0  # Frequency of bobbing (cycles per second)
        self.bob_time = 0.0  # Time tracker for bobbing effect
        self.bob_velocity = 0.0  # Speed for bobbing effect
        self.bob_sway = 0.0  # Horizontal sway effect
        self.bob_sway_speed = 1.0  # Speed of sway
        self.bob_sway_amplitude = 0.025  # Reduced amplitude of sway
        self.movement_keys_held = False  # Flag for movement keys
        self.bob_damping = 0.0  # Damping factor for smoother stop

        # Smoothing attributes
        self.smoothing_factor = 0.7  # Smoothing factor for camera movement
        self.smoothed_position = np.array(position, dtype='f4')  # Smoothed camera position
        self.smoothed_yaw = self.yaw  # Smoothed yaw
        self.smoothed_pitch = self.pitch  # Smoothed pitch

        self.update_camera_vectors()

    def update_camera_vectors(self):
        """Update the camera front, right, and up vectors based on yaw and pitch."""
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
        """Create a view matrix for the camera based on current position and orientation."""
        bobbing_height, bob_sway = self.calculate_bobbing()
        target_camera_position = self.position + np.array([bob_sway, bobbing_height, 0.0])

        # Smooth the camera position
        self.smoothed_position += (target_camera_position - self.smoothed_position) * self.smoothing_factor

        return np.array([
            self.right[0], self.up[0], -self.front[0], 0.0,
            self.right[1], self.up[1], -self.front[1], 0.0,
            self.right[2], self.up[2], -self.front[2], 0.0,
            -np.dot(self.right, self.smoothed_position), -np.dot(self.up, self.smoothed_position), np.dot(self.front, self.smoothed_position),
            1.0
        ], dtype='f4')

    def calculate_bobbing(self):
        """Calculate the camera bobbing effect based on movement."""
        if self.grounded and self.movement_keys_held and np.linalg.norm(self.velocity[:2]) > 0:
            self.bob_time += 0.016  # Increment time (approx 60 FPS)

            # Calculate bobbing effect
            bobbing_height = self.bob_amplitude * sin(self.bob_time * self.bob_frequency * 2 * pi)
            # Calculate horizontal sway effect
            self.bob_sway = self.bob_sway_amplitude * sin(self.bob_time * self.bob_sway_speed * 2 * pi)

            return bobbing_height, self.bob_sway
        else:
            # Gradually dampen the bobbing and sway effect when not moving
            self.bob_time = max(0.0, self.bob_time - self.bob_damping)  # Dampen the time
            bobbing_height = self.bob_amplitude * sin(self.bob_time * self.bob_frequency * 2 * pi)
            self.bob_sway *= (1.0 - self.bob_damping)  # Apply damping to sway

            return bobbing_height, self.bob_sway

    def process_mouse_movement(self, x_offset, y_offset, sensitivity=0.1):
        """Process mouse movement to update camera orientation."""
        self.yaw += x_offset * sensitivity
        self.pitch -= y_offset * sensitivity
        self.pitch = np.clip(self.pitch, -89.0, 89.0)  # Limit pitch

        # Smooth the yaw and pitch
        self.smoothed_yaw += (self.yaw - self.smoothed_yaw) * self.smoothing_factor
        self.smoothed_pitch += (self.pitch - self.smoothed_pitch) * self.smoothing_factor

        self.update_camera_vectors()

    def jump(self):
        """Make the player jump if grounded."""
        if self.grounded:
            self.velocity[1] = self.jump_force
            self.grounded = False  # Set to false after jumping

    def apply_gravity(self, delta_time):
        """Apply gravity to the player's vertical velocity."""
        if not self.grounded:
            self.velocity[1] += self.gravity * delta_time
        self.position[1] += self.velocity[1] * delta_time

    def update_velocity(self, forward_input, right_input, delta_time):
        """Update horizontal movement based on player input."""
        horizontal_front = np.array([self.front[0], 0.0, self.front[2]], dtype='f4')
        horizontal_front /= np.linalg.norm(horizontal_front)

        forward_acceleration = self.acceleration * forward_input
        right_acceleration = self.acceleration * right_input

        # Determine if movement keys are held
        self.movement_keys_held = forward_input != 0 or right_input != 0

        self.velocity[0] += right_acceleration * self.right[0] * delta_time
        self.velocity[2] += right_acceleration * self.right[2] * delta_time
        self.velocity[0] += forward_acceleration * horizontal_front[0] * delta_time
        self.velocity[2] += forward_acceleration * horizontal_front[2] * delta_time

        # Apply friction
        self.velocity[0] *= (1.0 - self.friction)
        self.velocity[2] *= (1.0 - self.friction)

        # Update position based on horizontal velocity
        self.position[0] += self.velocity[0] * delta_time
        self.position[2] += self.velocity[2] * delta_time

    def check_collision(self, min_bound, max_bound):
        """Check for collision with the specified bounding box."""
        player_min = np.array([
            self.position[0] - self.width / 2,
            self.position[1],
            self.position[2] - self.length / 2
        ])
        player_max = np.array([
            self.position[0] + self.width / 2,
            self.position[1] + self.height,
            self.position[2] + self.length / 2
        ])

        return (player_min[0] < max_bound[0] and player_max[0] > min_bound[0] and
                player_min[1] < max_bound[1] and player_max[1] > min_bound[1] and
                player_min[2] < max_bound[2] and player_max[2] > min_bound[2])

    def resolve_collision(self, min_bound, max_bound):
        """Resolve collision with the specified bounding box."""
        player_min = np.array([
            self.position[0] - self.width / 2,
            self.position[1],
            self.position[2] - self.length / 2
        ])
        player_max = np.array([
            self.position[0] + self.width / 2,
            self.position[1] + self.height,
            self.position[2] + self.length / 2
        ])

        overlap_x = min(max_bound[0] - player_min[0], player_max[0] - min_bound[0])
        overlap_y = min(max_bound[1] - player_min[1], player_max[1] - min_bound[1])
        overlap_z = min(max_bound[2] - player_min[2], player_max[2] - min_bound[2])

        # Resolve collision based on the smallest overlap
        if overlap_x < overlap_y and overlap_x < overlap_z:
            # Colliding with sides
            if self.position[0] < (min_bound[0] + max_bound[0]) / 2:
                self.position[0] -= overlap_x  # Move left
            else:
                self.position[0] += overlap_x  # Move right
            self.velocity[0] = 0  # Reset horizontal velocity
            self.grounded = False  # Not grounded when colliding with sides

        elif overlap_y < overlap_x and overlap_y < overlap_z:
            # Colliding with the top or bottom
            if self.position[1] < (min_bound[1] + max_bound[1]) / 2:
                self.position[1] -= overlap_y  # Move down (land on top)
                self.grounded = True  # Set grounded when landing
            else:
                self.position[1] += overlap_y  # Move up
            self.velocity[1] = 0  # Reset vertical velocity

        else:
            # Colliding with the front or back
            if self.position[2] < (min_bound[2] + max_bound[2]) / 2:
                self.position[2] -= overlap_z  # Move backward
            else:
                self.position[2] += overlap_z  # Move forward
            self.velocity[2] = 0  # Reset depth velocity
            self.grounded = False  # Not grounded when colliding with front or back

        # Check if the player is grounded based on Y position
        if player_min[1] <= min_bound[1]:  # Player is on the ground
            self.position[1] = min_bound[1] + self.height / 2  # Reset to ground level
            self.grounded = True  # Player is grounded on the ground

    def update_physics(self, delta_time, forward_input, right_input, min_bound, max_bound):
        """Update the player's physics, including movement and collision detection."""
        self.update_velocity(forward_input, right_input, delta_time)
        self.apply_gravity(delta_time)

        if self.check_collision(min_bound, max_bound):
            self.resolve_collision(min_bound, max_bound)

        # Check if the player is on the ground
        if self.position[1] <= min_bound[1] + self.height / 2:
            self.position[1] = min_bound[1] + self.height / 2  # Reset to ground level
            self.grounded = True  # Player is grounded on the ground
