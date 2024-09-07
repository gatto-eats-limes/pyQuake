#version 330

in vec2 fragUV;         // Texture coordinates from the vertex shader
in vec3 fragNormal;     // Normal from the vertex shader
in vec3 fragPosition;   // World-space position from the vertex shader
out vec4 fragColorOut;  // Final fragment color output

uniform sampler2D texture0;  // Texture sampler
uniform vec3 lightPos;       // Light position
uniform vec3 viewPos;        // Camera position

void main() {
    // Sample the texture color
    vec3 texColor = texture(texture0, fragUV).rgb;

    // Lighting calculations
    vec3 lightDir = normalize(lightPos - fragPosition);
    vec3 norm = normalize(fragNormal);

    // Ambient lighting
    vec3 ambient = 0.2 * texColor;

    // Diffuse lighting
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * texColor;

    // Specular lighting (Phong reflection model)
    vec3 viewDir = normalize(viewPos - fragPosition);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = spec * vec3(1.0); // White specular light

    // Combine the results
    vec3 result = ambient + diffuse + specular;
    fragColorOut = vec4(result, 1.0);  // Output final color with full opacity
}
