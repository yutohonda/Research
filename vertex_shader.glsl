#version 400 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 textureCoord;
out vec2 outTextureCoord;
uniform mat4 MVP;

void main(void) {
    outTextureCoord = textureCoord;
    gl_Position = MVP * vec4(position, 1.0);
}