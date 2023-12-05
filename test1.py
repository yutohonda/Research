import cv2
import pygetwindow as gw
import pyautogui
import numpy
# ウィンドウのタイトルを指定
window_title = "DownWell"

# ウィンドウの取得
target_window = gw.getWindowsWithTitle(window_title)[0]

target_window.activate()


#左端のスクリーン座標x,yを取得
x,y=target_window.topleft

#ウィンドウの幅と高さを取得
width,height=target_window.size

# スクリーンショットの取得
screenshot = pyautogui.screenshot(region=(x, y, width, height))

# スクリーンショットをOpenCVの画像に変換
screenshot_cv = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)

# スクリーンショットを表示
cv2.imshow("Window Capture", screenshot_cv)
cv2.waitKey(0)
cv2.destroyAllWindows()
