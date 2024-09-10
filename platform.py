import numpy as np
from PIL import Image
import moderngl


class Platform:
    def __init__(self, ctx, texture_path, width=8.0, length=8.0, height=1.0, tile_factor=(8.0, 8.0)):
        self.width = width
        self.length = length
        self.height = height
        self.tile_factor = tile_factor
        self.min_bound = np.array([-self.width / 2, 0, -self.length / 2], dtype='f4')
        self.max_bound = np.array([self.width / 2, self.height, self.length / 2], dtype='f4')

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
        vertices = np.array([
            # Bottom face (Y = 0)
            -self.width / 2, 0, -self.length / 2, 0, -1, 0, 0, 0,
            self.width / 2, 0, -self.length / 2, 0, -1, 0, self.tile_factor[0], 0,
            self.width / 2, 0, self.length / 2, 0, -1, 0, self.tile_factor[0], self.tile_factor[1],
            -self.width / 2, 0, self.length / 2, 0, -1, 0, 0, self.tile_factor[1],

            # Top face (Y = height)
            -self.width / 2, self.height, -self.length / 2, 0, 1, 0, 0, 0,
            self.width / 2, self.height, -self.length / 2, 0, 1, 0, self.tile_factor[0], 0,
            self.width / 2, self.height, self.length / 2, 0, 1, 0, self.tile_factor[0], self.tile_factor[1],
            -self.width / 2, self.height, self.length / 2, 0, 1, 0, 0, self.tile_factor[1],

            # Side faces (Y = 0 to height)
            # Front face
            -self.width / 2, 0, -self.length / 2, 0, 0, -1, 0, 0,
            self.width / 2, 0, -self.length / 2, 0, 0, -1, self.tile_factor[0], 0,
            self.width / 2, self.height, -self.length / 2, 0, 0, -1, self.tile_factor[0], self.tile_factor[1],
            -self.width / 2, self.height, -self.length / 2, 0, 0, -1, 0, self.tile_factor[1],

            # Back face
            -self.width / 2, 0, self.length / 2, 0, 0, 1, 0, 0,
            self.width / 2, 0, self.length / 2, 0, 0, 1, self.tile_factor[0], 0,
            self.width / 2, self.height, self.length / 2, 0, 0, 1, self.tile_factor[0], self.tile_factor[1],
            -self.width / 2, self.height, self.length / 2, 0, 0, 1, 0, self.tile_factor[1],

            # Left face
            -self.width / 2, 0, -self.length / 2, -1, 0, 0, 0, 0,
            -self.width / 2, 0, self.length / 2, -1, 0, 0, self.tile_factor[0], 0,
            -self.width / 2, self.height, self.length / 2, -1, 0, 0, self.tile_factor[0], self.tile_factor[1],
            -self.width / 2, self.height, -self.length / 2, -1, 0, 0, 0, self.tile_factor[1],

            # Right face
            self.width / 2, 0, -self.length / 2, 1, 0, 0, 0, 0,
            self.width / 2, 0, self.length / 2, 1, 0, 0, self.tile_factor[0], 0,
            self.width / 2, self.height, self.length / 2, 1, 0, 0, self.tile_factor[0], self.tile_factor[1],
            self.width / 2, self.height, -self.length / 2, 1, 0, 0, 0, self.tile_factor[1],
        ], dtype='f4')

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

        vbo = ctx.buffer(vertices.tobytes())
        ibo = ctx.buffer(indices.tobytes())
        program = ctx.program(
            vertex_shader=open('shaders/vertex_shader.glsl').read(),
            fragment_shader=open('shaders/fragment_shader.glsl').read()
        )
        vao = ctx.vertex_array(program, [(vbo, '3f 3f 2f', 'in_vert', 'in_normal', 'in_uv')], ibo)
        return vbo, ibo, vao

    def check_collision(self, player):
        player_min = player.position - np.array([player.width / 2, player.height / 2, player.length / 2])
        player_max = player.position + np.array([player.width / 2, player.height / 2, player.length / 2])

        tolerance = 0.01

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

        # Resolve the collision along the Y-axis first
        if overlap_y < overlap_x and overlap_y < overlap_z:
            if player.position[1] < self.min_bound[1]:  # Player is below the platform
                player.position[1] -= overlap_y  # Move the player down
            else:  # Player is above the platform
                player.position[1] += overlap_y  # Move the player up to prevent sticking
            player.grounded = True  # Set grounded state because the collision is from above
        else:
            # Handle X and Z axis collisions but do not set grounded state
            if overlap_x < overlap_z:
                if player.position[0] < self.min_bound[0]:  # Player is on the left side
                    player.position[0] -= overlap_x  # Move the player to the left
                elif player.position[0] > self.max_bound[0]:  # Player is on the right side
                    player.position[0] += overlap_x  # Move the player to the right
            else:  # Resolve along the Z axis (depth)
                if player.position[2] < self.min_bound[2]:  # Player is behind
                    player.position[2] -= overlap_z  # Move the player back
                elif player.position[2] > self.max_bound[2]:  # Player is in front
                    player.position[2] += overlap_z  # Move the player forward

        # Check if the player is on the sides (X or Z) and set grounded state accordingly
        if (player.position[0] < self.min_bound[0] + tolerance or
                player.position[0] > self.max_bound[0] - tolerance or
                player.position[2] < self.min_bound[2] + tolerance or
                player.position[2] > self.max_bound[2] - tolerance):
            player.grounded = False  # Player cannot jump if on the sides
        elif player.position[1] < self.max_bound[1] and player.position[1] > self.min_bound[1]:
            player.grounded = True  # Only set grounded if within the Y bounds of the platform

        return True

    def render(self, program, model_matrix, light_pos):
        program['model'].write(model_matrix.tobytes())
        program['lightPos'].value = tuple(light_pos)
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLES)
