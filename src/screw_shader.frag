#version 320 es
#undef lowp
#undef mediump
#undef highp

precision mediump float;

uniform vec4 FlagColor;
uniform vec3 LightPos;

in vec4 vertexColor;
in vec3 Normal;
in vec3 Position;

out vec4 fragColor;

void main() {
    float ambientStrength = 0.1f;
    vec4 lightColor = vec4(1.0, 1.0, 1.0, 1.0);
    
    vec4 ambient = ambientStrength * lightColor;
    
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(LightPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec4 diffuse = diff * lightColor;

    vec4 result = (diffuse + ambient) * FlagColor;

    fragColor = result;
}

