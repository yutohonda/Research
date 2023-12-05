import easyocr
import cv2
from PIL import ImageFont, ImageDraw, Image
import torch
import time
import threading

from OpenGL.GL import *
import glfw
import numpy as np
import glm

capIm = []
resultText = None
resultOcrIm = None
isActive = True

width = 1280
height = 720
    
### 文字認識
#OCRの処理
def ocrFunc():
    #GPUの設定　
    gpu = True if torch.cuda.is_available() else False
    reader = easyocr.Reader(['ja', 'en'], gpu = gpu) # this needs to run only once to load the model into memory
    global capIm
    global resultText
    global isActive
    
    while isActive:
        if len(capIm) > 0:
            resultText = reader.readtext(capIm)
        else:
            time.sleep(1)
       
#画像の処理　読み込み、文字の書き込み、表示
def imageFunc():
        
    #env\Scripts\activate.ps1
    #カメラの設定
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    #imagePath = str('testImage.png')
    global capIm
    global resultText
    global isActive
    global resultOcrIm
    
    while isActive:
        ###
        #capIm = cv2.imread(imagePath)
        ret, capIm = cap.read()
        capIm = cv2.cvtColor(capIm, cv2.COLOR_BGR2RGB)
        #imgをndarrayからPILに変換
        img_pil = Image.fromarray(capIm)

        while resultText is None:
            time.sleep(0.5)
            print("Waiting Text")
        
        
        for element in resultText:
            if element:
                text = element[1]
                #四隅の色の平均を求める
                rAve = 0; gAve = 0; bAve = 0
                rectPos = []
                for i in range(4):
                    pos = [int(element[0][i][0]), int(element[0][i][1])]
                    # 座標がはみ出す事があるので修正
                    if pos[0] < 0: pos[0] = 0
                    elif pos[0] > width - 1: pos[0] = width - 1
                    if pos[1] < 0: pos[1] = 0
                    elif pos[1] > height - 1: pos[1] = height - 1
                    
                    rectPos.append(pos)
                    #print(pos)
                    
                    posColor = img_pil.getpixel((pos[0], pos[1]))
                    rAve += posColor[0]
                    gAve += posColor[1]
                    bAve += posColor[2]
                
                rAve /= 4; gAve /= 4; bAve /= 4
                color = (int(rAve), int(gAve), int(bAve))
                
                #認識した文字を青で囲む
                #cv2.rectangle(img = capIm, pt1=pos1, pt2=pos3, color = (255, 0, 0))
                #認識した文字と確信度を赤で表示
                #capIm=putText_japanese(capIm, element[1]+':'+str(round(element[2], 2)), element[0][0], 20, (10, 10, 255))
                #capIm=putText_japanese(img_pil, element[1], element[0][0], 20, (10, 10, 255))
                
                font = ImageFont.truetype('PixelMplus12-Regular.ttf', 
                       size = int(abs(rectPos[0][0] - rectPos[2][0]) / (len(text) + 1) + 1) )
        
                #drawインスタンス生成
                draw = ImageDraw.Draw(img_pil)
                
                #塗りつぶし
                if rectPos[0][1] < rectPos[2][1]:
                    draw.rectangle(((rectPos[0][0], rectPos[0][1]), (rectPos[2][0], rectPos[2][1])), fill=color)
                
                #テキスト描画
                draw.text(xy = (int((rectPos[0][0] + rectPos[2][0]) / 2),
                                int((rectPos[0][1] + rectPos[2][1]) / 2)),
                        text = text,
                        fill=(0, 255, 0),
                        font=font,
                        anchor="mm",
                        spacing = 10,
                        )

        resultOcrIm = img_pil
        
    cap.release()
    
    
###　シェーダー
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
vertexShaderFile = "vertex_shader.glsl"
fragmentShaderFile = "fragment_shader.glsl"
tex_loc = -1
texture = None
texCoord_vbo = None

#外部ファイルからシェーダーを読み込む
def read_shader_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

vertex_shader_src = read_shader_from_file(vertexShaderFile)
fragment_shader_src= read_shader_from_file(fragmentShaderFile)

def create_texture():
    #img = Image.open(image_file_path)
    textureData = resultOcrIm.tobytes()
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
    if resultOcrIm.mode == "RGB":
        format = GL_RGB
    glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, textureData)
    return texture

def update_texture():
    global texture
    texture = create_texture()
    
    
    
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
    texture = create_texture()
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

SCREEN_WIDTH = width
SCREEN_HEIGHT = height

def shaderMain():
    global isActive
    
    while resultOcrIm is None:
        print("WaitingOCR")
        time.sleep(0.5)
        
        
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
        
        update_texture()

        update(window, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw()

        glfw.swap_buffers(window)

        glfw.poll_events()

    isActive = False
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    thread_image = threading.Thread(target=imageFunc)
    thread_ocr = threading.Thread(target=ocrFunc)
    thread_shader = threading.Thread(target=shaderMain)
    thread_image.start()
    thread_ocr.start()
    thread_shader.start()
    thread_image.join()
    thread_ocr.join()
    thread_shader.join()