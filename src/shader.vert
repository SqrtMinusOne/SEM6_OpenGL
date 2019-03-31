//layout (location = 0) in vec3 VertexPosition;

varying vec4 vertex_color;
void main(){
    vec4 pos = vec4(gl_Vertex);
    pos.y = pos.y * (0.5 + 0.5);

    gl_Position = gl_ModelViewProjectionMatrix * pos;
    vertex_color = gl_Color;
}

