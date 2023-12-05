from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv2
import numpy as np
import sys
from PIL import Image

# シェーダープログラム
vertex_shader = """
#version 330 core
in vec2 position;
out vec2 texCoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    texCoord = position * 0.5 + 0.5;;
}
"""

fragment_shader = """
#version 330 core
in vec2 texCoord;
out vec4 fragColor;
uniform sampler2D tex;
void main()
{
    vec4 color = texture(tex, texCoord);
    float grayscale = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    fragColor = vec4(grayscale, grayscale, grayscale, color.a);
}
"""
# 画像を読み込む
image = Image.open('testImage.png')
image = image.transpose(Image.FLIP_TOP_BOTTOM)  # 上下反転
w, h = image.size
# ウィンドウサイズ
window_width, window_height = w * 5, h * 5

#　初期化
glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(window_width, window_height)
glutCreateWindow(b"OpenGL Image Processing")

# シェーダープログラムをコンパイル
def compile_shader(shader, shader_type):
    shader_id = glCreateShader(shader_type)
    glShaderSource(shader_id, shader)
    glCompileShader(shader_id)
    if not glGetShaderiv(shader_id, GL_COMPILE_STATUS):
        raise Exception("Shader compilation error: " + glGetShaderInfoLog(shader_id).decode())
    return shader_id

vertex_shader_id = compile_shader(vertex_shader, GL_VERTEX_SHADER)
fragment_shader_id = compile_shader(fragment_shader, GL_FRAGMENT_SHADER)

# プログラムオブジェクトを作成
shader_program = glCreateProgram()
glAttachShader(shader_program, vertex_shader_id)
#glDeleteShader(vertex_shader_id)
glAttachShader(shader_program, fragment_shader_id)
#glDeleteShader(fragment_shader_id)
glLinkProgram(shader_program)
glUseProgram(shader_program)

# テクスチャを作成
texture_id = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture_id)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
image_data = np.array(image)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

# 頂点データ
vertices = np.array([
    -1.0, -1.0,
    1.0, -1.0,
    1.0, 1.0,
    -1.0, 1.0,
], dtype=np.float32)
# テクスチャ座標
tex_coords = np.array([
    0.0, 1.0,
    1.0, 1.0,
    1.0, 0.0,
    0.0, 1.0,
], dtype=np.float32)

# VAOを作成
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# VBOを作成
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

# 頂点属性を有効化
position_loc = glGetAttribLocation(shader_program, "position")
glEnableVertexAttribArray(position_loc)
glVertexAttribPointer(position_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

# メインループ
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glUniform1i(glGetUniformLocation(shader_program, "tex"), 0)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glutSwapBuffers()


glutDisplayFunc(display)
glutMainLoop()
