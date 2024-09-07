#version 330

in vec3 fragColor;
in vec3 fragNormal;
in vec3 fragPosition;
out vec4 fragColorOut;

uniform vec3 lightPos;
uniform vec3 viewPos;

void main() {
    vec3 lightDir = normalize(lightPos - fragPosition);
    vec3 norm = normalize(fragNormal);

    // Ambient light
    vec3 ambient = 0.2 * fragColor;

    // Diffuse light
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * fragColor;

    // Specular light
    vec3 viewDir = normalize(viewPos - fragPosition);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = spec * vec3(1.0); // White specular light

    // Combine results
    vec3 result = ambient + diffuse + specular;
    fragColorOut = vec4(result, 1.0);
}
