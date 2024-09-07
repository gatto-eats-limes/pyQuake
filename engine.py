import pygame
import moderngl
import numpy as np
from camera import Player  # Ensure this imports your Player class correctly

class ScrunkEngine:
    def __init__(self, width=800, height=600):
        self.width, self.height = width, height
        self.last_mouse_pos = None

        pygame.init()
        pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("3D Cube with Camera", "")

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.prog = self.create_program()
        self.vbo, self.ibo, self.vao = self.create_buffers()
        self.projection = self.create_projection_matrix()
        self.prog['projection'].write(self.projection)

        self.player = Player([0.0, 5.0, 0.0], [0.0, 1.0, 0.0])
        self.prog['view'].write(self.player.create_view_matrix())

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.center_mouse()

    def create_program(self):
        try:
            vertex_shader = self.load_shader("shaders/vertex_shader.glsl")
            fragment_shader = self.load_shader("shaders/fragment_shader.glsl")

            prog = self.ctx.program(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader
            )
            return prog

        except Exception as e:
            print("Shader compilation failed:", e)
            raise

    def load_shader(self, filepath):
        """Loads shader code from an external file."""
        with open(filepath, 'r') as file:
            return file.read()

    def create_buffers(self):
        vertices = np.array([
            # Front face
            -0.5, -0.5,  0.5,  0.0, 0.0, 1.0, 1.0, 0.0, 0.0,  # Vertex data: x, y, z, nx, ny, nz, r, g, b
             0.5, -0.5,  0.5,  0.0, 0.0, 1.0, 0.0, 1.0, 0.0,
             0.5,  0.5,  0.5,  0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 0.0, 1.0, 1.0, 1.0, 0.0,

            # Back face
            -0.5, -0.5, -0.5,  0.0, 0.0, -1.0, 1.0, 0.0, 1.0,
             0.5, -0.5, -0.5,  0.0, 0.0, -1.0, 1.0, 1.0, 1.0,
             0.5,  0.5, -0.5,  0.0, 0.0, -1.0, 0.0, 1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 0.0, -1.0, 1.0, 1.0, 0.0,

            # Left face
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            -0.5, -0.5,  0.5, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            -0.5,  0.5,  0.5, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
            -0.5,  0.5, -0.5, -1.0, 0.0, 0.0, 1.0, 0.0, 1.0,

            # Right face
            0.5, -0.5, -0.5,  1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5,  0.5,  1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            0.5,  0.5,  0.5,  1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
            0.5,  0.5, -0.5,  1.0, 0.0, 0.0, 1.0, 1.0, 1.0,

            # Top face
            -0.5, 0.5, -0.5,  0.0, 1.0, 0.0, 1.0, 0.0, 0.0,
             0.5, 0.5, -0.5,  0.0, 1.0, 0.0, 1.0, 1.0, 0.0,
             0.5, 0.5,  0.5,  0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, 0.5,  0.5,  0.0, 1.0, 0.0, 0.0, 0.0, 1.0,

            # Bottom face
            -0.5, -0.5, -0.5,  0.0, -1.0, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, -0.5,  0.0, -1.0, 0.0, 1.0, 1.0, 0.0,
             0.5, -0.5,  0.5,  0.0, -1.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0, 0.0, 0.0, 0.0, 1.0,
        ], dtype='f4')

        indices = np.array([
            # Front face
            0, 1, 2, 0, 2, 3,
            # Back face
            4, 5, 6, 4, 6, 7,
            # Left face
            8, 9, 10, 8, 10, 11,
            # Right face
            12, 13, 14, 12, 14, 15,
            # Top face
            16, 17, 18, 16, 18, 19,
            # Bottom face
            20, 21, 22, 20, 22, 23,
        ], dtype='i4')

        vbo = self.ctx.buffer(vertices.tobytes())
        ibo = self.ctx.buffer(indices.tobytes())

        vao = self.ctx.vertex_array(self.prog, [(vbo, '3f 3f 3f', 'in_vert', 'in_normal', 'in_color')], ibo)
        return vbo, ibo, vao

    def create_projection_matrix(self):
        aspect_ratio = self.width / self.height
        fov = 50.0
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
            right_input = -1  # Move left
        if keys[pygame.K_d]:
            right_input = 1   # Move right
        if keys[pygame.K_w]:
            forward_input = 1  # Move forward
        if keys[pygame.K_s]:
            forward_input = -1  # Move backward

        self.player.update_velocity(forward_input, right_input, delta_time)

        if keys[pygame.K_SPACE] and self.player.grounded:
            self.player.jump()
            self.player.grounded = False

    def handle_mouse_movement(self):
        mouse_pos = pygame.mouse.get_pos()
        x_offset = mouse_pos[0] - self.last_mouse_pos[0]
        y_offset = mouse_pos[1] - self.last_mouse_pos[1]
        self.player.process_mouse_movement(x_offset, y_offset)
        self.center_mouse()

    def check_collisions(self):
        min_bound = np.array([-0.5, -0.5, -0.5], dtype='f4')
        max_bound = np.array([0.5, 0.5, 0.5], dtype='f4')

        if self.player.check_collision(min_bound, max_bound):
            self.player.resolve_collision(min_bound, max_bound)
            print("Collision detected and resolved.")

    def apply_gravity(self, delta_time):
        self.player.velocity[1] -= 9.81 * delta_time
        self.player.position += self.player.velocity * delta_time

    def render(self):
        self.ctx.clear(0.1, 0.1, 0.1)
        self.prog['view'].write(self.player.create_view_matrix())
        self.prog['model'].write(np.identity(4, dtype='f4'))
        self.prog['lightPos'].value = (2.0, 2.0, 2.0)
        self.prog['viewPos'].value = tuple(self.player.position)
        self.vao.render(moderngl.TRIANGLES)
        pygame.display.flip()

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
            self.check_collisions()

            self.render()

        pygame.quit()

if __name__ == "__main__":
    engine = ScrunkEngine()
    engine.main_loop()