#pip install mss
import mss

bbox = GetWindowRectFromName(TargetWindowTitle)

def SCT(bbox):
    with mss.mss() as sct:
        img = sct.grab(bbox)
    return img
