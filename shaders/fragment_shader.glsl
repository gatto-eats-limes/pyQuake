#version 330 core

in vec2 fragUV;          // Texture coordinates
in vec3 fragNormal;      // Transformed normal
in vec3 fragPosition;    // World position

out vec4 fragColorOut;   // Final output color

uniform sampler2D texture0; // Texture sampler
uniform vec3 lightPos;      // Light source position

void main() {
    vec3 texColor = texture(texture0, fragUV).rgb; // Sample the texture using UV coordinates

    vec3 lightDir = normalize(lightPos - fragPosition); // Direction to light source
    vec3 norm = normalize(fragNormal); // Normal at the fragment

    // Ambient and diffuse lighting
    vec3 ambient = 0.32 * texColor; // Ambient light contribution
    float diff = max(dot(norm, lightDir), 0.0); // Diffuse lighting factor
    vec3 diffuse = diff * texColor; // Diffuse contribution

    vec3 result = ambient + diffuse; // Final color
    fragColorOut = vec4(result, 1.0); // Set the output color
}
