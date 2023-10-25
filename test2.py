import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import torch
import time
import threading


im = []
result = []
isRunning = True
    
def ocrFunc():
    #GPUの設定　
    gpu = True if torch.cuda.is_available() else False
    reader = easyocr.Reader(['ja', 'en'], gpu = gpu) # this needs to run only once to load the model into memory
    global im
    global result
    global isRunning
    
    while isRunning:
        if len(im) > 0:
            result = reader.readtext(im)
        else:
            time.sleep(1)
       
    
    
#メインの処理
def imageFunc():
        
    #env\Scripts\activate.ps1
    #カメラの設定
    cap = cv2.VideoCapture(1)
    width, height = 640, 360
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    #imagePath = str('testImage.png')
    global im
    global result
    global isRunning
    
    while isRunning:
        ###
        #im = cv2.imread(imagePath)
        ret, im = cap.read()
        
        #imgをndarrayからPILに変換
        img_pil = Image.fromarray(im)

        for element in result:
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
                #cv2.rectangle(img = im, pt1=pos1, pt2=pos3, color = (255, 0, 0))
                #認識した文字と確信度を赤で表示
                #im=putText_japanese(im, element[1]+':'+str(round(element[2], 2)), element[0][0], 20, (10, 10, 255))
                #im=putText_japanese(img_pil, element[1], element[0][0], 20, (10, 10, 255))
                
                font = ImageFont.truetype('ItalicCute.ttf', 
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

        #PILからndarrayに変換して返す
        resultIm = np.array(img_pil)
            
        cv2.imshow('result', resultIm)
        #cv2.imwrite('result.png', im)
        key =cv2.waitKey(30)
        if key == 27:
            isRunning = False
            break
        
    cap.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    thread_image = threading.Thread(target=imageFunc)
    thread_ocr = threading.Thread(target=ocrFunc)
    thread_image.start()
    thread_ocr.start()
    thread_image.join()
    thread_ocr.join()
    

