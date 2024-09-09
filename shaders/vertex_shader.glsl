#version 330

in vec3 in_vert;        // Vertex position
in vec3 in_normal;      // Vertex normal
in vec2 in_uv;          // Texture coordinates

out vec2 fragUV;        // Pass texture coordinates to fragment shader
out vec3 fragNormal;    // Pass transformed normal to fragment shader
out vec3 fragPosition;  // Pass world position to fragment shader

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec4 worldPosition = model * vec4(in_vert, 1.0);
    gl_Position = projection * view * worldPosition;

    fragUV = in_uv;
    fragNormal = normalize(mat3(model) * in_normal);
    fragPosition = vec3(worldPosition);
}
