def main(window_title="YouTube"):

    TargetWindowTitle = GetTitle(window_title)

    While True:
        try:
            bbox = GetWindowRectFromName(TargetWindowTitle)

            img = SCT(bbox)

            face_rects, track_window = FaceDetection(img)

            x, y, w, h = track_window
            img2 = cv2.rectangle(img, pt1=(x, y), pt2=(x+w, y+h), color=(0, 0, 255), thickness=5)
            img_show("window", img2, position=(
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

