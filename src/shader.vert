#version 320 es

layout (location = 0) in vec3 VertexPosition;

uniform mat4 MVP;

void main(){
    vec4 pos = vec4(VertexPosition, 1.0); 
    pos.z = pos.z * pos.y;
    gl_Position = MVP * pos;
}

