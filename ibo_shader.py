from OpenGL.GL import *
import glfw
import numpy as np

vert_pos = np.array([
    [-0.5, -0.5, 0.0],  # 頂点 0
    [0.5, -0.5, 0.0],   # 頂点 1
    [0.5, 0.5, 0.0],    # 頂点 2
    [-0.5, 0.5, 0.0]],  # 頂点 3
    dtype=np.float32)
tria_index = np.array(
    [[0, 1, 2],  # フェース0
    [2, 3, 0]],  # フェース1
    dtype=np.uint32)
program = None
pos_vbo = None
face_ibo = None

vertex_shader_src="""
#version 400 core

layout(location = 0) in vec3 position;

void main(void) {
    gl_Position = vec4(position, 1.0);
}
""".strip()

fragment_shader_src="""
#version 400 core

out vec4 outFragmentColor;

void main(void) {
    outFragmentColor = vec4(1.0);
}
""".strip()

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
    program = create_program(vertex_shader_src, fragment_shader_src)
    pos_vbo = create_vbo(vert_pos)
    face_ibo = create_ibo(tria_index)

def update(window, width, height):
    pass

def draw():
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, face_ibo)
    num_vertex = tria_index.size  # 6
    glDrawElements(GL_TRIANGLES, num_vertex, GL_UNSIGNED_INT, None)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glUseProgram(0)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    if not glfw.init():
        return

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
