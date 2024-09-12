import json
import pygame
import moderngl
import numpy as np
from player import Player
from platform import Platform

class RyanEngine:
    def __init__(self, width=800, height=600, scene_file='scenes/testing.json'):
        self.width, self.height = width, height
        self.last_mouse_pos = None

        pygame.init()
        pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Ryan Manning 3D Engine")

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.platforms = []
        self.player = None
        self.load_scene(scene_file)  # Load the scene during initialization
        self.projection = self.create_projection_matrix()
        self.light_pos = np.array([10.0, 10.0, 10.0], dtype='f4')

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.center_mouse()

    def load_scene(self, scene_file):
        """Load platforms and the player from a scene file."""
        with open(scene_file, 'r') as f:
            scene_data = json.load(f)

        # Load platforms
        for platform_data in scene_data['platforms']:
            position = platform_data['position']
            texture_top = platform_data['texture_top']
            texture_side = platform_data['texture_side']
            platform = Platform(self.ctx, texture_top, texture_side)
            platform.position = np.array(position, dtype='f4')  # Set the platform position
            self.platforms.append(platform)

        # Load player
        if 'player' in scene_data:
            player_data = scene_data['player']
            player_position = player_data['position']
            self.player = Player(player_position, [0.0, 1.0, 0.0])
            self.player.velocity = np.array(player_data['velocity'], dtype='f4')
            self.player.rotation = np.array(player_data['rotation'], dtype='f4')

    def create_projection_matrix(self):
        aspect_ratio = self.width / self.height
        fov = 90.0
        near, far = 0.1, 100.0
        f = 1.0 / np.tan(np.radians(fov) / 2.0)
        return np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), -1],
            [0, 0, (2 * far * near) / (near - far), 0]
        ], dtype='f4')

    def center_mouse(self):
        pygame.mouse.set_pos(self.width // 2, self.height // 2)
        self.last_mouse_pos = pygame.mouse.get_pos()

    def handle_input(self, delta_time):
        keys = pygame.key.get_pressed()
        forward_input = 0
        right_input = 0

        if keys[pygame.K_a]:
            right_input = -1
        if keys[pygame.K_d]:
            right_input = 1
        if keys[pygame.K_w]:
            forward_input = 1
        if keys[pygame.K_s]:
            forward_input = -1

        self.player.update_velocity(forward_input, right_input, delta_time)

        # Jumping logic: Check if space is pressed and player is grounded
        if keys[pygame.K_SPACE]:
            self.player.jump()

    def handle_mouse_movement(self):
        mouse_pos = pygame.mouse.get_pos()
        x_offset = mouse_pos[0] - self.last_mouse_pos[0]
        y_offset = mouse_pos[1] - self.last_mouse_pos[1]
        self.player.process_mouse_movement(x_offset, y_offset)
        self.center_mouse()

    def apply_gravity(self, delta_time):
        self.player.apply_gravity(delta_time)

    def render(self):
        self.ctx.clear(0.1, 0.1, 0.1)

        # Bind the projection and view matrices
        self.player.view_matrix = self.player.create_view_matrix()
        program = self.platforms[0].vao.program  # Assuming you're using the first platform
        program['view'].write(self.player.view_matrix.tobytes())
        program['projection'].write(self.projection.tobytes())

        # Render each platform or collidable object
        for platform in self.platforms:
            model_matrix = np.eye(4, dtype='f4')  # Identity matrix for now
            platform.render(program, model_matrix, self.light_pos)

        pygame.display.flip()

    def check_collisions(self):
        """Check for collisions with all platforms."""
        for platform in self.platforms:
            if platform.check_collision(self.player):
                break  # Exit after finding a collision
        else:
            self.player.grounded = False  # Reset grounded state if no collision is detected

    def main_loop(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            delta_time = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_input(delta_time)
            self.handle_mouse_movement()
            self.apply_gravity(delta_time)

            # Check collision with all platforms
            self.check_collisions()

            self.render()

        pygame.quit()

if __name__ == "__main__":
    engine = RyanEngine()
    engine.main_loop()
