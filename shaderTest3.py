import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

def load_texture():
    img = Image.open("testImage.png")
    w, h = img.size
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)

    glEnable(GL_TEXTURE_2D)

    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(90.0, 0.0, 0.0, 1.0)

    glBegin(GL_QUADS)
    glTexCoord2d(0.0, 1.0)
    glVertex3d(-0.5, -0.5,  0.0)
    glTexCoord2d(1.0, 1.0)
    glVertex3d( 0.5, -0.5,  0.0)
    glTexCoord2d(1.0, 0.0)
    glVertex3d( 0.5,  0.5,  0.0)
    glTexCoord2d(0.0, 0.0)
    glVertex3d(-0.5,  0.5,  0.0)
    glEnd()

    glPopMatrix()

    glDisable(GL_TEXTURE_2D)

    glDisable(GL_BLEND)

    glFlush()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(300, 300)
    glutCreateWindow(b"TextureSample1")
    glutDisplayFunc(display)
    glClearColor(0.0, 0.0, 1.0, 1.0)

    load_texture()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glutMainLoop()

if __name__ == '__main__':
    main()