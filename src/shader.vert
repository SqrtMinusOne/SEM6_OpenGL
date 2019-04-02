#version 320 es

layout (location = 0) in vec3 VertexPosition;

uniform mat4 ModelViewMatrix;
uniform mat4 MVP;
uniform float Time;

out vec3 Normal;
out vec3 Position;


void main(){
    float k = 0.1;
    vec4 pos = vec4(VertexPosition, 1.); 
    pos.z = pos.z + k * sin((pos.x + Time) * 20.);
    Position = vec4(ModelViewMatrix * pos).xyz;
    
    vec3 norm = vec3(0.0);
    float angle = atan(-1. / (k * cos((pos.x + Time) * 20.)));
    norm.x = 1. * cos(angle);
    norm.z = 1. * sin(angle);
    if (norm.z < 0.){
        norm.x = norm.x * -1.;
        norm.z = norm.z * -1.;
    }
    norm.y = 0.;
    Normal = norm;
    
    gl_Position = MVP * pos;

}
