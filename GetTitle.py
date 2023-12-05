#pip install ahk
from ahk import AHK

window_title = "YouTube"

def GetTitle(window_title):
    ahk = AHK()
    wins = list(ahk.windows())
    titles = [win.title for win in wins]
    for t in titles:
        text = t.decode("shift-jis", errors="ignore")
        #print(text)
        if window_title in text:
            return text


import ctypes
from ctypes.wintypes import HWND, DWORD, RECT

TargetWindowTitle = GetTitle(window_title)

def GetWindowRectFromName(TargetWindowTitle):
    TargetWindowHandle = ctypes.windll.user32.FindWindowW(0, TargetWindowTitle)
    Rectangle = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(
        TargetWindowHandle, ctypes.pointer(Rectangle))
    return (Rectangle.left, Rectangle.top, Rectangle.right, Rectangle.bottom)


#pip install mss
import mss

bbox = GetWindowRectFromName(TargetWindowTitle)

def SCT(bbox):
    with mss.mss() as sct:
        img = sct.grab(bbox)
    return img


#pip install opencv-python
#curl https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml > haarcascade_frontalface_default.xml
import cv2

img = SCT(bbox)

def FaceDetection(img):
    face_cascade = cv2.CascadeClassifier(
        'haarcascade_frontalface_default.xml')
    face_rects = face_cascade.detectMultiScale(img)
    (face_x, face_y, w, h) = tuple(face_rects[0])
    track_window = (face_x, face_y, w, h)

    roi = img[face_y:face_y+h, face_x:face_x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
    rect, track_window = cv2.meanShift(dst, track_window, term_crit)

    return face_rects, track_window


def main(window_title="YouTube"):

    TargetWindowTitle = GetTitle(window_title)

    while True:
        try:
            bbox = GetWindowRectFromName(TargetWindowTitle)

            img = SCT(bbox)

            face_rects, track_window = FaceDetection(img)

            x, y, w, h = track_window
            img2 = cv2.rectangle(img, pt1=(x, y), pt2=(x+w, y+h), color=(0, 0, 255), thickness=5)
            cv2.imshow("window", img2, position=(
                        bbox[0]*2-bbox[2], bbox[1]-30), size=(bbox[2]-bbox[0], bbox[3]-bbox[1]))

            # escape sequence
            # ESC to escape
            k = cv2.waitKey(1) & 0xFF
            if k == 27:         # wait for ESC key to exit
                cv2.destroyAllWindows()
                return
            # or topleft mouse to escape
            if AHK().mouse_position == (0, 0):
                cv2.destroyAllWindows()
                return
        except:
            continue


