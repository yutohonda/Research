import cv2

#カメラの設定　デバイスIDは0

cap = cv2.VideoCapture(1)
#print(cap)
#繰り返しのためのwhile文
while True:
    #カメラからの画像取得
    
    ret, frame = cap.read()

    #カメラの画像の出力
    if ret:
        cv2.imshow('camera' , frame)
    else:
        print("sippai")

    #繰り返し分から抜けるためのif文
    key =cv2.waitKey(10)
    if key == 27:
        break

#メモリを解放して終了するためのコマンド
cap.release()
cv2.destroyAllWindows()
