#version 320 es

layout (location = 0) in vec3 VertexPosition;

uniform mat4 MVP;
uniform float Time;

void main(){
    vec4 pos = vec4(VertexPosition, 1.0); 
    pos.z = pos.z + 0.1 * cos((pos.x + Time) * 20.);
    gl_Position = MVP * pos;
}

