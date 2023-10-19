import numpy as np
from PIL import Image
import cv2
from matplotlib import pyplot as plt
from time import time_ns
import numpy as np
import math


class Camera:
    # Usual camera ID's
    DEFAULT_CAM_ID = 0
    GO_PRO_ID = 2

    def __init__(self, capture_device_id=0, frame_width=640,
                  frame_height=480, fps=24, actual_QR_text="O",
                    display_video_capture=False, draw_overlay=False,
                      flip_image=False):
        """Initialize and setup camera for video capture. Start a QR detectector.

        :param capture_device_id: ID of the Camera; should be an integer >= 0.
          ID 0 is for default camera, defaults to 0
        """
        self.__cam = cv2.VideoCapture(capture_device_id)
        self.__QR_code_detector = cv2.QRCodeDetector()
        self.__frame_width = frame_width
        self.__frame_height = frame_height
        self.__fps = fps

        # set camera resolution and fps
        self.__cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.__frame_width)
        self.__cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.__frame_height)
        self.__cam.set(cv2.CAP_PROP_FPS, self.__fps)

        # place holder for image frame 
        self.__image = np.zeros((self.__frame_height, self.__frame_width, 3))

        # QR data
        self.__actual_QR_text = actual_QR_text
        self.__QR_text = None
        self.__QR_border_points = np.zeros((1, 4, 2))

        self.__display_capture = display_video_capture
        self.__draw_overlay = display_video_capture and draw_overlay
        self.__flip_image = flip_image

        self.__x_tl, self.__y_tl = 0, 0
        self.__x_tr, self.__y_tr = 0, 0
        self.__x_br, self.__y_br = 0, 0
        self.__x_bl, self.__y_bl = 0, 0
        self.__img_ctr_x = -1
        self.__img_ctr_y = -1

    def __update_frame(self):
        ret, self.__image = self.__cam.read()
        self.__frame_height, self.__frame_width = self.__image.shape[:2]
        if ret:
            return True
        return False

    def __QR_detect_and_decode(self):
        self.__QR_text, self.__QR_border_points, binarized_QR = self.__QR_code_detector.detectAndDecode(self.__image)

    def __find_QR_center(self):
        if self.__QR_text == self.__actual_QR_text:    
            self.__x_tl, self.__y_tl = self.__QR_border_points[0, 0]
            self.__x_tr, self.__y_tr = self.__QR_border_points[0, 1]
            self.__x_br, self.__y_br = self.__QR_border_points[0, 2]
            self.__x_bl, self.__y_bl = self.__QR_border_points[0, 3]
            self.__img_ctr_x = int((self.__x_bl + self.__x_br + self.__x_tl + self.__x_tr)//4)
            self.__img_ctr_y = int((self.__y_bl + self.__y_br + self.__y_tl + self.__y_tr)//4)
            return True
        self.__x_tl, self.__y_tl = 0, 0
        self.__x_tr, self.__y_tr = 0, 0
        self.__x_br, self.__y_br = 0, 0
        self.__x_bl, self.__y_bl = 0, 0
        self.__img_ctr_x = -1
        self.__img_ctr_y = -1
        return False
    
    def __display_video_and_overlay(self):
        if self.__draw_overlay:
            cv2.line(self.__image, tuple(map(lambda x: int(x), [self.__x_tl, self.__y_tl])), tuple(map(lambda x: int(x), [self.__x_tr, self.__y_tr])), (255,0,0), 5)
            cv2.line(self.__image, tuple(map(lambda x: int(x), [self.__x_tr, self.__y_tr])), tuple(map(lambda x: int(x), [self.__x_br, self.__y_br])), (0,255,0), 5)
            cv2.line(self.__image, tuple(map(lambda x: int(x), [self.__x_br, self.__y_br])), tuple(map(lambda x: int(x), [self.__x_bl, self.__y_bl])), (0,0,255), 5)
            cv2.line(self.__image, tuple(map(lambda x: int(x), [self.__x_bl, self.__y_bl])), tuple(map(lambda x: int(x), [self.__x_tl, self.__y_tl])), (255,0,255), 5)
            cv2.line(self.__image, (0, 0), (self.__img_ctr_x, self.__img_ctr_y), (255,0,0), 5)

        if self.__display_capture:
            if self.__flip_image:
                self.__image[:, :, :] = cv2.flip(self.__image, 1)
            cv2.imshow('frame', self.__image)
            cv2.waitKey(1)

    def __del__(self):
        self.__cam.release()
        cv2.destroyAllWindows()

    def run(self):
        if not self.__update_frame(): 
            print("Video capture error, no frame returned")
        self.__QR_detect_and_decode()
        if not self.__find_QR_center() and self.__QR_text != "": 
            print(f"The detected QR text: {self.__QR_text} did not match the desired text: {self.__actual_QR_text}.")
        self.__display_video_and_overlay()

        x = None
        y = None
        heading = None
        if self.__img_ctr_x != -1 or self.__img_ctr_y != -1:
            x = self.__frame_width//2 - self.__img_ctr_x
            y = self.__frame_height//2 - self.__img_ctr_y

            ctr_of_QR_top_line = self.__img_ctr_x - (self.__x_tl + self.__x_tr)//2, self.__img_ctr_y - (self.__y_tl + self.__y_tr)//2
            heading = math.atan2(ctr_of_QR_top_line[1], ctr_of_QR_top_line[0]) - math.pi/2
        return x, y, heading


if __name__ == "__main__":
    cam = Camera(2, display_video_capture=False, draw_overlay=False, flip_image=False, actual_QR_text="D")
    while True:
        print(cam.run())