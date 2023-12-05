import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import torch
import time
import threading


capIm = []
ocrResult = []
isActive = True

#OCRの処理
def ocrFunc():
    #GPUの設定　
    gpu = True if torch.cuda.is_available() else False
    reader = easyocr.Reader(['ja', 'en'], gpu = gpu) # this needs to run only once to load the model into memory
    global capIm
    global ocrResult
    global isActive
    
    while isActive:
        if len(capIm) > 0:
            ocrResult = reader.readtext(capIm)
        else:
            time.sleep(1)
       
def colorDistance(color1: tuple[int, int, int], color2: tuple[int, int, int]):
    cd = (color1[0] - color2[0]) ** 2 + (color1[1] - color2[1]) ** 2 + (color1[2] - color2[2]) ** 2
    return cd
    
#画像の処理　読み込み、文字の書き込み、表示
def imageFunc():
        
    sampleNum = 5
    #env\Scripts\activate.ps1
    #カメラの設定
    cap = cv2.VideoCapture(1)
    width, height = 800, 450
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    #imagePath = str('testImage.png')
    global capIm
    global ocrResult
    global isActive
    
    while isActive:
        ###
        #capIm = cv2.imread(imagePath)
        ret, capIm = cap.read()
        
        #imgをndarrayからPILに変換
        img_pil = Image.fromarray(capIm)
        #drawインスタンス生成
        draw = ImageDraw.Draw(img_pil)
                
        # テキスト、テキストボックスの描画
        for element in ocrResult:
            if element:
                text = element[1]
                
                # テキストボックス
                # 四隅の色の平均を求める
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
                    # print(pos)
                    
                    posColor = img_pil.getpixel((pos[0], pos[1]))
                    rAve += posColor[0]
                    gAve += posColor[1]
                    bAve += posColor[2]
                
                rAve /= 4; gAve /= 4; bAve /= 4
                textBoxCol = (int(rAve), int(gAve), int(bAve))
                
                # 文字色設定
                samplePosInter = (int((rectPos[2][0] - rectPos[0][0]) / (sampleNum + 1)), 
                                  int((rectPos[2][1] - rectPos[0][1]) / (sampleNum + 1)))
                textCol = (0, 0, 0)
                textColDistance = 0
                textPos = (0,0)
                for i in range (1, sampleNum + 1):
                    samplePos = (rectPos[0][0] + samplePosInter[0] * i, rectPos[0][1] + samplePosInter[1] * i)
                    sampleCol = img_pil.getpixel(samplePos)
                    
                    # テキストボックスとの色差を求め大きい方を残す
                    tsampleColDistance = colorDistance(sampleCol, textBoxCol)
                    if(tsampleColDistance > textColDistance): 
                        textColDistance = tsampleColDistance
                        textCol = sampleCol
                        textPos = samplePos
                
                #塗りつぶし
                
                if rectPos[0][1] < rectPos[2][1]:
                    draw.rectangle(((rectPos[0][0], rectPos[0][1]), (rectPos[2][0], rectPos[2][1])), fill=textBoxCol)
                
                #テキスト描画
                font = ImageFont.truetype('PixelMplus12-Regular.ttf', 
                                        size = int(abs(rectPos[0][0] - rectPos[2][0]) / (len(text) + 1) + 1) )
        
                draw.text(xy = (int((rectPos[0][0] + rectPos[2][0]) / 2),
                                int((rectPos[0][1] + rectPos[2][1]) / 2)),
                        text = text,
                        fill= textCol,
                        font=font,
                        anchor="mm",
                        spacing = 10,
                        )
                
                # 文字色設定　位置確認用
                
                #draw.rectangle(((rectPos[0][0], rectPos[0][1]), (rectPos[2][0], rectPos[2][1])), None, (255, 0, 0))
                r = 2
                draw.rectangle((textPos[0] - r, textPos[1] - r, textPos[0] + r, textPos[1] + r),(0, 255, 0)) 
                print(text + str(textPos) + str(textCol) + str(textColDistance))
                
        font = ImageFont.truetype('ItalicCute.ttf', 30)
        draw.text(xy = (100, 20),text = ("サンプル数:" + str(sampleNum)), fill=(0,255,0), font=font, anchor="mm", spacing= 10)
        
        # 画面表示
        #PILからndarrayに変換して返す
        resultIm = np.array(img_pil)
        cv2.imshow('result', resultIm)
        #cv2.imwrite('result.png', capIm)
        key = cv2.waitKey(30)
        if key == ord("w"):
            sampleNum += 1
        
        if key == ord("s"):
            if sampleNum > 1:
                sampleNum -= 1
            
        if key == 27:
            isActive = False
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
    

