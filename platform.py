import numpy as np
from PIL import Image
import moderngl


class Platform:
    def __init__(self, ctx, texture_path, width=4.0, length=4.0, height=0.5):
        self.width = width
        self.length = length
        self.height = height
        self.min_bound = np.array([-self.width / 2, -self.height / 2, -self.length / 2], dtype='f4')
        self.max_bound = np.array([self.width / 2, self.height / 2, self.length / 2], dtype='f4')

        # Load the texture
        self.texture = self.load_texture(ctx, texture_path)
        self.vbo, self.ibo, self.vao = self.create_buffers(ctx)

    def load_texture(self, ctx, filepath):
        img = Image.open(filepath).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        texture = ctx.texture(img.size, 3, img.tobytes())
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        texture.use(0)
        return texture

    def create_buffers(self, ctx):
        # Define vertices: positions, normals, and texture coordinates
        vertices = np.array([
            # Positions                  # Normals          # Texture Coordinates
            -self.width / 2, 0, -self.length / 2, 0, 1, 0, 0, 0,  # Bottom left
            self.width / 2, 0, -self.length / 2, 0, 1, 0, 1, 0,  # Bottom right
            self.width / 2, 0, self.length / 2, 0, 1, 0, 1, 1,  # Top right
            -self.width / 2, 0, self.length / 2, 0, 1, 0, 0, 1  # Top left
        ], dtype='f4')

        # Define indices for two triangles to form a square
        indices = np.array([
            0, 1, 2,  # First triangle
            0, 2, 3  # Second triangle
        ], dtype='i4')

        # Create Vertex Buffer Object (VBO) and Index Buffer Object (IBO)
        vbo = ctx.buffer(vertices.tobytes())
        ibo = ctx.buffer(indices.tobytes())

        # Create the shader program
        program = ctx.program(
            vertex_shader=open('shaders/vertex_shader.glsl').read(),
            fragment_shader=open('shaders/fragment_shader.glsl').read()
        )

        # Create a Vertex Array Object (VAO)
        vao = ctx.vertex_array(program, [(vbo, '3f 3f 2f', 'in_vert', 'in_normal', 'in_uv')], ibo)
        return vbo, ibo, vao

    def check_collision(self, player):
        player_min = player.position - np.array([player.width / 2, player.height / 2, player.length / 2])
        player_max = player.position + np.array([player.width / 2, player.height / 2, player.length / 2])

        # Check for collision
        if (player_min[0] < self.max_bound[0] and player_max[0] > self.min_bound[0] and
                player_min[1] < self.max_bound[1] and player_max[1] > self.min_bound[1] and
                player_min[2] < self.max_bound[2] and player_max[2] > self.min_bound[2]):
            return True
        return False

    def render(self, program, model_matrix, light_pos):
        program['model'].write(model_matrix.tobytes())
        program['lightPos'].value = tuple(light_pos)
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLES)
