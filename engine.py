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

        self.camera = Camera([0.0, 0.0, 3.0], [0.0, 1.0, 0.0])

        self.prog['view'].write(self.camera.create_view_matrix())

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.center_mouse()

    def create_program(self):
        return self.ctx.program(
            vertex_shader="""
            #version 330
            in vec3 in_vert;
            in vec3 in_normal; 
            in vec3 in_color;
            out vec3 fragColor;
            out vec3 fragNormal; 
            out vec3 fragLightDir; 

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main() {
                gl_Position = projection * view * model * vec4(in_vert, 1.0);
                fragColor = in_color;
                fragNormal = normalize(mat3(model) * in_normal); 
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 fragColor;
            in vec3 fragNormal;
            in vec3 fragLightDir; 
            out vec4 fragColorOut;

            uniform vec3 lightPos; 
            uniform vec3 viewPos;  

            void main() {
                vec3 lightDir = normalize(lightPos - fragNormal);
                vec3 norm = normalize(fragNormal);

                vec3 ambient = 0.1 * fragColor;

                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = diff * fragColor;

                vec3 viewDir = normalize(viewPos - fragNormal);
                vec3 reflectDir = reflect(-lightDir, norm);
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
                vec3 specular = vec3(1.0) * spec;

                vec3 result = ambient + diffuse + specular;
                fragColorOut = vec4(result, 1.0);
            }
            """
        )

    def create_buffers(self):
        vbo = self.ctx.buffer(np.array([
             0.0,  0.5,  0.0,   0.0, 0.0, 1.0, 1.0, 0.0, 0.0,  # R, Vertex 0
            -0.5, -0.5,  0.5,   0.0, 0.0, 1.0, 0.5, 1.0, 0.5,  # G, Vertex 1
             0.5, -0.5,  0.5,   0.0, 0.0, 1.0, 0.5, 0.5, 1.0,  # B, Vertex 2
             0.5, -0.5, -0.5,   0.0, 0.0, 1.0, 1.0, 1.0, 0.5,  # Y, Vertex 3
            -0.5, -0.5, -0.5,   0.0, 0.0, 1.0, 1.0, 0.5, 0.5,  # C, Vertex 4
        ], dtype='f4').tobytes())

        ibo = self.ctx.buffer(np.array([
            0, 1, 2,
            0, 2, 3,
            0, 3, 4,
            0, 4, 1,
            1, 2, 3,
            1, 3, 4,
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

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.camera.strafe(-1, 0.05)
        if keys[pygame.K_d]:
            self.camera.strafe(1, 0.05)
        if keys[pygame.K_w]:
            self.camera.move_forward(0.05)
        if keys[pygame.K_s]:
            self.camera.move_forward(-0.05)

    def handle_mouse_movement(self):
        mouse_pos = pygame.mouse.get_pos()
        x_offset = mouse_pos[0] - self.last_mouse_pos[0]
        y_offset = mouse_pos[1] - self.last_mouse_pos[1]
        self.camera.process_mouse_movement(x_offset, y_offset)
        self.center_mouse()

    def run(self):
        clock = pygame.time.Clock()

        self.prog['lightPos'].value = (6, 6, 6)
        self.prog['viewPos'].value = self.camera.position

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.handle_input()
            self.handle_mouse_movement()

            self.ctx.clear(0.1, 0.1, 0.1)
            self.ctx.clear(depth=1.0)

            self.prog['view'].write(self.camera.create_view_matrix())

            model = np.identity(4, dtype='f4')
            self.prog['model'].write(model.tobytes())

            self.vao.render(moderngl.TRIANGLES)
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    engine = ScrunkEngine()
    engine.run()
