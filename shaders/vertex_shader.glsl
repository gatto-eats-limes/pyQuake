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
