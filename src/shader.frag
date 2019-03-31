#version 320 es
#undef lowp
#undef mediump
#undef highp

precision mediump float;

uniform vec3 FlagColor;
in vec3 vertexColor;
out vec3 fragColor;

void main() {
    fragColor = FlagColor;
}

