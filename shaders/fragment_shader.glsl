#version 330

in vec2 fragUV;          // Texture coordinates
in vec3 fragNormal;      // Transformed normal
in vec3 fragPosition;    // World position

out vec4 fragColorOut;   // Final output color

uniform sampler2D texture0; // Texture sampler
uniform vec3 lightPos;      // Light source position
uniform vec3 viewPos;       // Camera position

void main() {
    vec3 texColor = texture(texture0, fragUV).rgb;

    vec3 lightDir = normalize(lightPos - fragPosition);
    vec3 norm = normalize(fragNormal);
    vec3 viewDir = normalize(viewPos - fragPosition);

    float levels = 4.0;
    float scale = 1.0 / levels;

    vec3 ambient = 0.2 * texColor;

    float diff = max(dot(norm, lightDir), 0.0);
    diff = floor(diff / scale) * scale;  // Step-based lighting for toon shading
    vec3 diffuse = diff * texColor;

    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    spec = floor(spec / scale) * scale;  // Step-based specular for toon shading
    vec3 specular = spec * vec3(1.0);  // White specular

    vec3 result = ambient + diffuse + specular;
    fragColorOut = vec4(result, 1.0);
}
