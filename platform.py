import numpy as np
from PIL import Image
import moderngl


class Platform:
    def __init__(self, ctx, texture_path, width=8.0, length=8.0, height=1.0, tile_factor=(8.0, 8.0)):
        self.width = width
        self.length = length
        self.height = height  # Height of the platform
        self.tile_factor = tile_factor
        self.min_bound = np.array([-self.width / 2, 0, -self.length / 2], dtype='f4')  # Updated for correct Y min
        self.max_bound = np.array([self.width / 2, self.height, self.length / 2],
                                  dtype='f4')  # Updated for correct Y max

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
        # Define vertices for the platform
        vertices = np.array([
            # Bottom face (Y = 0)
            -self.width / 2, 0, -self.length / 2, 0, -1, 0, 0, 0,  # Bottom left
            self.width / 2, 0, -self.length / 2, 0, -1, 0, self.tile_factor[0], 0,  # Bottom right
            self.width / 2, 0, self.length / 2, 0, -1, 0, self.tile_factor[0], self.tile_factor[1],  # Top right
            -self.width / 2, 0, self.length / 2, 0, -1, 0, 0, self.tile_factor[1],  # Top left

            # Top face (Y = height)
            -self.width / 2, self.height, -self.length / 2, 0, 1, 0, 0, 0,  # Bottom left
            self.width / 2, self.height, -self.length / 2, 0, 1, 0, self.tile_factor[0], 0,  # Bottom right
            self.width / 2, self.height, self.length / 2, 0, 1, 0, self.tile_factor[0], self.tile_factor[1],
            # Top right
            -self.width / 2, self.height, self.length / 2, 0, 1, 0, 0, self.tile_factor[1],  # Top left

            # Side faces (Y = 0 to height)
            # Front face
            -self.width / 2, 0, -self.length / 2, 0, 0, -1, 0, 0,  # Bottom left
            self.width / 2, 0, -self.length / 2, 0, 0, -1, self.tile_factor[0], 0,  # Bottom right
            self.width / 2, self.height, -self.length / 2, 0, 0, -1, self.tile_factor[0], self.tile_factor[1],
            # Top right
            -self.width / 2, self.height, -self.length / 2, 0, 0, -1, 0, self.tile_factor[1],  # Top left

            # Back face
            -self.width / 2, 0, self.length / 2, 0, 0, 1, 0, 0,  # Bottom left
            self.width / 2, 0, self.length / 2, 0, 0, 1, self.tile_factor[0], 0,  # Bottom right
            self.width / 2, self.height, self.length / 2, 0, 0, 1, self.tile_factor[0], self.tile_factor[1],
            # Top right
            -self.width / 2, self.height, self.length / 2, 0, 0, 1, 0, self.tile_factor[1],  # Top left

            # Left face
            -self.width / 2, 0, -self.length / 2, -1, 0, 0, 0, 0,  # Bottom left
            -self.width / 2, 0, self.length / 2, -1, 0, 0, self.tile_factor[0], 0,  # Bottom right
            -self.width / 2, self.height, self.length / 2, -1, 0, 0, self.tile_factor[0], self.tile_factor[1],
            # Top right
            -self.width / 2, self.height, -self.length / 2, -1, 0, 0, 0, self.tile_factor[1],  # Top left

            # Right face
            self.width / 2, 0, -self.length / 2, 1, 0, 0, 0, 0,  # Bottom left
            self.width / 2, 0, self.length / 2, 1, 0, 0, self.tile_factor[0], 0,  # Bottom right
            self.width / 2, self.height, self.length / 2, 1, 0, 0, self.tile_factor[0], self.tile_factor[1],
            # Top right
            self.width / 2, self.height, -self.length / 2, 1, 0, 0, 0, self.tile_factor[1],  # Top left
        ], dtype='f4')

        # Define indices for two triangles per face to form the full platform
        indices = np.array([
            # Bottom face
            0, 1, 2,
            0, 2, 3,

            # Top face
            4, 5, 6,
            4, 6, 7,

            # Front face
            8, 9, 10,
            8, 10, 11,

            # Back face
            12, 13, 14,
            12, 14, 15,

            # Left face
            16, 17, 18,
            16, 18, 19,

            # Right face
            20, 21, 22,
            20, 22, 23,
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

        # Allow for a slight margin for collision detection
        tolerance = 0.01  # Adjust as necessary

        # Check for collision in each dimension
        collision = (
                player_min[0] < self.max_bound[0] + tolerance and player_max[0] > self.min_bound[0] - tolerance and
                player_min[1] < self.max_bound[1] + tolerance and player_max[1] > self.min_bound[1] - tolerance and
                player_min[2] < self.max_bound[2] + tolerance and player_max[2] > self.min_bound[2] - tolerance
        )

        if not collision:
            return False

        # Collision resolution
        overlap_x = min(player_max[0] - self.min_bound[0], self.max_bound[0] - player_min[0])
        overlap_y = min(player_max[1] - self.min_bound[1], self.max_bound[1] - player_min[1])
        overlap_z = min(player_max[2] - self.min_bound[2], self.max_bound[2] - player_min[2])

        # Determine which axis to resolve based on the smallest overlap
        if overlap_x < overlap_y and overlap_x < overlap_z:
            if player.position[0] < self.min_bound[0]:  # Player is on the left side
                player.position[0] -= overlap_x
            else:  # Player is on the right side
                player.position[0] += overlap_x
        elif overlap_y < overlap_x and overlap_y < overlap_z:
            if player.position[1] < self.min_bound[1]:  # Player is below
                player.position[1] -= overlap_y
            else:  # Player is above
                player.position[1] += overlap_y
        else:  # Resolve along the Z axis (depth)
            if player.position[2] < self.min_bound[2]:  # Player is behind
                player.position[2] -= overlap_z
            else:  # Player is in front
                player.position[2] += overlap_z

        return True

    def render(self, program, model_matrix, light_pos):
        program['model'].write(model_matrix.tobytes())
        program['lightPos'].value = tuple(light_pos)
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLES)
