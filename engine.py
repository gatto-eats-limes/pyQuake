import pygame
import moderngl
import numpy as np
from camera import Player  # Ensure this imports your Player class correctly

# fun
class ScrunkEngine:
    def __init__(self, width=800, height=600):
        self.last_mouse_pos = None
        pygame.init()
        pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("3D but scrunkly", "")

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.width, self.height = width, height

        self.prog = self.create_program()
        self.vbo, self.ibo, self.vao = self.create_buffers()
        self.projection = self.create_projection_matrix()
        self.prog['projection'].write(self.projection)

        self.player = Player([0.0, 1.0, 3.0], [0.0, 1.0, 0.0])
        self.prog['view'].write(self.player.create_view_matrix())

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.center_mouse()

    def create_program(self):
        try:
            prog = self.ctx.program(
                vertex_shader="""
                #version 330
                in vec3 in_vert;
                in vec3 in_normal; 
                in vec3 in_color;
                out vec3 fragColor;
                out vec3 fragNormal; 
                out vec3 fragPosition;

                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 projection;

                void main() {
                    vec4 worldPosition = model * vec4(in_vert, 1.0);
                    gl_Position = projection * view * worldPosition;
                    fragColor = in_color;
                    fragNormal = normalize(mat3(model) * in_normal); 
                    fragPosition = vec3(worldPosition);
                }
                """,
                fragment_shader="""
                #version 330
                in vec3 fragColor;
                in vec3 fragNormal;
                in vec3 fragPosition;
                out vec4 fragColorOut;

                uniform vec3 lightPos; 
                uniform vec3 viewPos;  

                void main() {
                    vec3 lightDir = normalize(lightPos - fragPosition);
                    vec3 norm = normalize(fragNormal);

                    vec3 ambient = 0.2 * fragColor; // Increased ambient lighting

                    float diff = max(dot(norm, lightDir), 0.0);
                    vec3 diffuse = diff * fragColor;

                    vec3 viewDir = normalize(viewPos - fragPosition);
                    vec3 reflectDir = reflect(-lightDir, norm);
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
                    vec3 specular = spec * vec3(1.0);

                    vec3 result = ambient + diffuse + specular;
                    fragColorOut = vec4(result, 1.0);
                }
                """
            )
            return prog

        except Exception as e:
            print("Shader compilation failed:", e)
            raise

    def create_buffers(self):
        # Define a cube (6 faces, 2 triangles per face)
        vbo = self.ctx.buffer(np.array([
            # Front face
            -0.5, -0.5,  0.5,  0.0, 0.0, 1.0, 0.0, 0.0, 0.5,
             0.5, -0.5,  0.5,  0.0, 0.0, 1.0, 1.0, 0.0, 0.5,
             0.5,  0.5,  0.5,  0.0, 0.0, 1.0, 1.0, 1.0, 0.5,
             0.5,  0.5,  0.5,  0.0, 0.0, 1.0, 1.0, 1.0, 0.5,
            -0.5,  0.5,  0.5,  0.0, 0.0, 1.0, 0.0, 1.0, 0.5,
            -0.5, -0.5,  0.5,  0.0, 0.0, 1.0, 0.0, 0.0, 0.5,

            # Back face
            -0.5, -0.5, -0.5,  0.0, 0.0, -1.0, 0.0, 0.0, 0.5,
             0.5, -0.5, -0.5,  0.0, 0.0, -1.0, 1.0, 0.0, 0.5,
             0.5,  0.5, -0.5,  0.0, 0.0, -1.0, 1.0, 1.0, 0.5,
             0.5,  0.5, -0.5,  0.0, 0.0, -1.0, 1.0, 1.0, 0.5,
            -0.5,  0.5, -0.5,  0.0, 0.0, -1.0, 0.0, 1.0, 0.5,
            -0.5, -0.5, -0.5,  0.0, 0.0, -1.0, 0.0, 0.0, 0.5,

            # Left face
            -0.5, -0.5, -0.5,  -1.0, 0.0, 0.0, 0.0, 0.0, 0.5,
            -0.5, -0.5,  0.5,  -1.0, 0.0, 0.0, 0.0, 0.0, 0.5,
            -0.5,  0.5,  0.5,  -1.0, 0.0, 0.0, 0.0, 1.0, 0.5,
            -0.5,  0.5,  0.5,  -1.0, 0.0, 0.0, 0.0, 1.0, 0.5,
            -0.5,  0.5, -0.5,  -1.0, 0.0, 0.0, 1.0, 1.0, 0.5,
            -0.5, -0.5, -0.5,  -1.0, 0.0, 0.0, 1.0, 0.0, 0.5,

            # Right face
             0.5, -0.5, -0.5,   1.0, 0.0, 0.0, 0.0, 0.0, 0.5,
             0.5, -0.5,  0.5,   1.0, 0.0, 0.0, 0.0, 0.0, 0.5,
             0.5,  0.5,  0.5,   1.0, 0.0, 0.0, 0.0, 1.0, 0.5,
             0.5,  0.5,  0.5,   1.0, 0.0, 0.0, 0.0, 1.0, 0.5,
             0.5,  0.5, -0.5,   1.0, 0.0, 0.0, 1.0, 1.0, 0.5,
             0.5, -0.5, -0.5,   1.0, 0.0, 0.0, 1.0, 0.0, 0.5,

            # Bottom face
            -0.5, -0.5, -0.5,   0.0, -1.0, 0.0, 0.0, 0.0, 0.5,
             0.5, -0.5, -0.5,   0.0, -1.0, 0.0, 1.0, 0.0, 0.5,
             0.5, -0.5,  0.5,   0.0, -1.0, 0.0, 1.0, 1.0, 0.5,
             0.5, -0.5,  0.5,   0.0, -1.0, 0.0, 1.0, 1.0, 0.5,
            -0.5, -0.5,  0.5,   0.0, -1.0, 0.0, 0.0, 1.0, 0.5,
            -0.5, -0.5, -0.5,   0.0, -1.0, 0.0, 0.0, 0.0, 0.5,

            # Top face
            -0.5,  0.5, -0.5,   0.0, 1.0, 0.0, 0.0, 0.0, 0.5,
             0.5,  0.5, -0.5,   0.0, 1.0, 0.0, 1.0, 0.0, 0.5,
             0.5,  0.5,  0.5,   0.0, 1.0, 0.0, 1.0, 1.0, 0.5,
             0.5,  0.5,  0.5,   0.0, 1.0, 0.0, 1.0, 1.0, 0.5,
            -0.5,  0.5,  0.5,   0.0, 1.0, 0.0, 0.0, 1.0, 0.5,
            -0.5,  0.5, -0.5,   0.0, 1.0, 0.0, 0.0, 0.0, 0.5,
        ], dtype='f4').tobytes())

        ibo = self.ctx.buffer(np.array([
            0, 1, 2,  0, 2, 3,  # Front face
            4, 5, 6,  4, 6, 7,  # Back face
            8, 9, 10, 8, 10, 11,  # Left face
            12, 13, 14, 12, 14, 15,  # Right face
            16, 17, 18, 16, 18, 19,  # Bottom face
            20, 21, 22, 20, 22, 23   # Top face
        ], dtype='i4').tobytes())

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

        # Jump only if the player is grounded
        if keys[pygame.K_SPACE] and self.player.grounded:
            self.player.jump()
            self.player.grounded = False  # Set grounded to false as the player is now jumping

    def handle_mouse_movement(self):
        mouse_pos = pygame.mouse.get_pos()
        x_offset = mouse_pos[0] - self.last_mouse_pos[0]
        y_offset = mouse_pos[1] - self.last_mouse_pos[1]
        self.player.process_mouse_movement(x_offset, y_offset)
        self.center_mouse()

    def check_collisions(self):
        # Define the cube's collision bounds
        min_bound = np.array([-0.5, -0.5, -0.5], dtype='f4')
        max_bound = np.array([0.5, 0.5, 0.5], dtype='f4')

        # Check for collision with the top face of the cube
        player_height = 1.0  # Assume player has height 1.0
        player_bottom_y = self.player.position[1] - (player_height / 2)
        player_top_y = self.player.position[1] + (player_height / 2)

        cube_top_y = max_bound[1]

        # Check if the player is within the horizontal bounds of the cube
        if (player_bottom_y < cube_top_y) and (player_top_y > min_bound[1]) and \
           (self.player.position[0] > min_bound[0] and self.player.position[0] < max_bound[0]) and \
           (self.player.position[2] > min_bound[2] and self.player.position[2] < max_bound[2]):

            # Resolve collision: Move the player on top of the cube
            self.player.position[1] = cube_top_y + (player_height / 2)
            self.player.velocity[1] = 0  # Reset vertical velocity upon landing
            self.player.grounded = True  # Indicate that the player is grounded
            print("Collision detected with the top face!")

    def apply_gravity(self, delta_time):
        if not self.player.grounded:
            self.player.velocity[1] -= 9.81 * delta_time  # Gravity effect when not grounded
        self.player.position += self.player.velocity * delta_time  # Update player position

    def run(self):
        clock = pygame.time.Clock()

        try:
            self.prog['lightPos'].value = (6, 6, 6)
            self.prog['viewPos'].value = tuple(self.player.position)

            while True:
                delta_time = clock.tick(60) / 1000.0  # Time in seconds

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                self.handle_input(delta_time)
                self.apply_gravity(delta_time)  # Apply gravity to the player
                self.handle_mouse_movement()

                self.check_collisions()  # Check for collisions with the cube

                self.ctx.clear(0.1, 0.1, 0.1)
                self.ctx.clear(depth=1.0)

                self.prog['view'].write(self.player.create_view_matrix())

                model = np.identity(4, dtype='f4')
                self.prog['model'].write(model.tobytes())

                self.vao.render(moderngl.TRIANGLES)

                pygame.display.flip()
        except KeyError as e:
            print(f"Uniform error: {e}")
            pygame.quit()

if __name__ == "__main__":
    engine = ScrunkEngine()
    engine.run()
