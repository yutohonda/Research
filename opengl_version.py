from OpenGL.GL import *
import glfw

def main():
    if not glfw.init():
        return

    window = glfw.create_window(640, 480, 'PyOpenGL Sample', None, None)
    if not window:
        glfw.terminate()
        print('Failed to create window')
        return

    glfw.make_context_current(window)

    # OpenGL の情報を表示
    print('Vendor:', glGetString(GL_VENDOR).decode('utf-8'))
    print('GPU:', glGetString(GL_RENDERER).decode('utf-8'))
    print('OpenGL version:', glGetString(GL_VERSION).decode('utf-8'))
    print('GLSL version:', glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8'))

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()