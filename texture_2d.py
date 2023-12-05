from OpenGL.GL import *
import glfw
import numpy as np
import glm
from PIL import Image

# 頂点を４つ用意
vert_pos = np.array([
    [-1, -1, 0.0],  # 頂点 0
    [1, -1, 0.0],   # 頂点 1
    [1, 1, 0.0],    # 頂点 2
    [-1, 1, 0.0]],  # 頂点 3
    dtype=np.float32)
# 四角形＝三角形２枚の頂点情報
tria_index = np.array(
    [[0, 1, 2],  # フェース0
    [2, 3, 0]],  # フェース1
    dtype=np.uint32)
tex_coords = np.array([
    0.0, 1.0,   # 頂点 0
    1.0, 1.0,   # 頂点 1
    1.0, 0.0,   # 頂点 2
    0.0, 0.0],  # 頂点 3
    dtype=np.float32)
program = None
# VBO:vertex buffer object ここでは頂点座標値を格納 
pos_vbo = None
# IBO:index buffer object  
face_ibo = None
png_file = "testImage.png"
vertexShaderFile = "vertex_shader.glsl"
fragmentShaderFile = "fragment_shader.glsl"
tex_loc = -1
texture = None
texCoord_vbo = None
img = Image.open(png_file)

#外部ファイルからシェーダーを読み込む
def read_shader_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

vertex_shader_src = read_shader_from_file(vertexShaderFile)
fragment_shader_src= read_shader_from_file(fragmentShaderFile)

def create_texture(image_file_path):
    #img = Image.open(image_file_path)
    width, height = img.size
    textureData = img.tobytes()
    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # WRAP_S は横方向にテクスチャをどのように延長するか
    # WRAP_T は縦方向にテクスチャをどのように延長するか
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # _MAG_FILTER は拡大時のフィルタの種類
    # _MIN_FILTER は縮小時のフィルタの種類
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    format = GL_RGBA
    if img.mode == "RGB":
        format = GL_RGB
    glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, textureData)
    return texture
    
def create_program(vertex_shader_src, fragment_shader_src):
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_src)
    glCompileShader(vertex_shader)
    result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if not result:
        err_str = glGetShaderInfoLog(vertex_shader).decode('utf-8')
        raise RuntimeError(err_str)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_src)
    glCompileShader(fragment_shader)
    result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if not result:
        err_str = glGetShaderInfoLog(fragment_shader).decode('utf-8')
        raise RuntimeError(err_str)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glDeleteShader(vertex_shader)
    glAttachShader(program, fragment_shader)
    glDeleteShader(fragment_shader)
    glLinkProgram(program)
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        err_str = glGetProgramInfoLog(program).decode('utf-8')
        raise RuntimeError(err_str)

    return program

def create_vbo(vertex):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo

def create_ibo(vert_index):
    ibo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, vert_index.nbytes, vert_index, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    return ibo

def init(window, width, height):
    global program, pos_vbo, face_ibo
    global texCoord_vbo, tex_loc, texture
    texture = create_texture(png_file)
    program = create_program(vertex_shader_src, fragment_shader_src)
    tex_loc = glGetUniformLocation(program, "texture0")
    pos_vbo = create_vbo(vert_pos)
    texCoord_vbo = create_vbo(tex_coords)
    face_ibo = create_ibo(tria_index)
    # MVP行列をユニフォーム変数に渡す
    #aspect_ratio = width / height  # 1.333
    aspect_ratio = 1.0
    M = glm.mat4(1.0)
    V = glm.lookAt(
        glm.vec3(0.0, 0.0, 1.0),  # 視点の位置
        glm.vec3(0.0, 0.0, 0.0),  # 注目点
        glm.vec3(0.0, 1.0, 0.0))  # カメラの上方向
    P = glm.ortho(
        -1.0 * aspect_ratio,  # 左位置
        1.0 * aspect_ratio,   # 右位置
        -1.0,                 # 下位置
        1.0,                  # 上位置
        0.1,                  # ニア面位置
        2.0)                  # ファー面位置
    MVP = np.array(P * V * M, dtype=np.float32)
    MVP_loc = glGetUniformLocation(program, "MVP")
    glUseProgram(program)
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
    glUseProgram(0)

def update(window, width, height):
    pass

def draw():
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glEnable(GL_TEXTURE_2D)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, texCoord_vbo)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, face_ibo)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)
    glUniform1i(tex_loc, 0)
    num_vertex = tria_index.size  # 6
    glDrawElements(GL_TRIANGLES, num_vertex, GL_UNSIGNED_INT, None)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glUseProgram(0)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    if not glfw.init():
        return

    SCREEN_WIDTH,SCREEN_HEIGHT = img.size
    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "PyOpenGL Sample", None, None)
    if not window:
        glfw.terminate()
        print('Failed to create window')
        return

    glfw.make_context_current(window)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    init(window, SCREEN_WIDTH, SCREEN_HEIGHT)

    while not glfw.window_should_close(window):
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        update(window, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw()

        glfw.swap_buffers(window)

        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()