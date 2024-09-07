#version 330

in vec3 in_vert;        // Vertex position
in vec3 in_normal;      // Vertex normal
in vec2 in_uv;          // Texture coordinates

out vec2 fragUV;        // Pass the texture coordinates to the fragment shader
out vec3 fragNormal;    // Pass the transformed normal to the fragment shader
out vec3 fragPosition;  // Pass the world position to the fragment shader

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Calculate the world position of the vertex
    vec4 worldPosition = model * vec4(in_vert, 1.0);

    // Set the position of the current vertex in clip space
    gl_Position = projection * view * worldPosition;

    // Pass the texture coordinates to the fragment shader
    fragUV = in_uv;

    // Transform the normal to world space and pass it to the fragment shader
    fragNormal = normalize(mat3(model) * in_normal);

    // Pass the world-space position to the fragment shader
    fragPosition = vec3(worldPosition);
}
