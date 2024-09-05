import pygame
import moderngl
import numpy as np
from camera import Camera

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

        self.camera = Camera([0.0, 1.0, 3.0], [0.0, 1.0, 0.0])
        self.prog['view'].write(self.camera.create_view_matrix())

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
        # Define a square (two triangles)
        vbo = self.ctx.buffer(np.array([
             0.5,  0.5,  0.0,   0.0, 0.0, 1.0, 1.0, 0.0, 0.0,  # Vertex 0 (top right)
            -0.5,  0.5,  0.0,   0.0, 0.0, 1.0, 0.0, 0.0, 1.0,  # Vertex 1 (top left)
            -0.5, -0.5,  0.0,   0.0, 0.0, 1.0, 0.0, 1.0, 0.5,  # Vertex 2 (bottom left)
             0.5, -0.5,  0.0,   0.0, 0.0, 1.0, 1.0, 1.0, 0.5,  # Vertex 3 (bottom right)
        ], dtype='f4').tobytes())

        ibo = self.ctx.buffer(np.array([
            0, 1, 2,  # First triangle
            0, 2, 3   # Second triangle
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

        self.camera.update_velocity(forward_input, right_input, delta_time)

        if keys[pygame.K_SPACE] and self.camera.grounded:
            self.camera.jump()

    def handle_mouse_movement(self):
        mouse_pos = pygame.mouse.get_pos()
        x_offset = mouse_pos[0] - self.last_mouse_pos[0]
        y_offset = mouse_pos[1] - self.last_mouse_pos[1]
        self.camera.process_mouse_movement(x_offset, y_offset)
        self.center_mouse()

    def run(self):
        clock = pygame.time.Clock()

        try:
            self.prog['lightPos'].value = (6, 6, 6)
            self.prog['viewPos'].value = tuple(self.camera.position)  # Convert position to a tuple

            while True:
                delta_time = clock.tick(60) / 1000.0  # Time in seconds

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                self.handle_input(delta_time)
                self.camera.apply_gravity(delta_time)  # Apply gravity to the camera
                self.handle_mouse_movement()

                self.ctx.clear(0.1, 0.1, 0.1)
                self.ctx.clear(depth=1.0)

                self.prog['view'].write(self.camera.create_view_matrix())

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
