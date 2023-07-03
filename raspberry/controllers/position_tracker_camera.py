import numpy as np
from PIL import Image
import cv2
from matplotlib import pyplot as plt
from time import time_ns


vid = cv2.VideoCapture(0)
qrCodeDetector = cv2.QRCodeDetector()
img_ctr_x = None
img_ctr_y = None

while True:
    start = time_ns()
    ret, image = vid.read()

    try:
        img_h, img_w, img_ch = image.shape
        x_max = img_w//2
        y_max = img_h//2
        # cv2.imwrite("raspberry/controllers/tape.png", image)

        # image = cv2.imread('raspberry/controllers/tape.png')

        decodedText, points, _ = qrCodeDetector.detectAndDecode(image)
        x_tl, y_tl = points[0, 0]
        x_tr, y_tr = points[0, 1]
        x_br, y_br = points[0, 2]
        x_bl, y_bl = points[0, 3]
        img_ctr_x = int((x_bl + x_br + x_tl + x_tr)//4)
        img_ctr_y = int((y_bl + y_br + y_tl + y_tr)//4)
        # cv2.line(image, tuple(map(lambda x: int(x), points[0][0])), tuple(map(lambda x: int(x), points[0][1])), (255,0,0), 5)
        # cv2.line(image, tuple(map(lambda x: int(x), points[0][1])), tuple(map(lambda x: int(x), points[0][2])), (255,0,0), 5)
        # cv2.line(image, tuple(map(lambda x: int(x), points[0][2])), tuple(map(lambda x: int(x), points[0][3])), (255,0,0), 5)
        # cv2.line(image, tuple(map(lambda x: int(x), points[0][3])), tuple(map(lambda x: int(x), points[0][0])), (255,0,0), 5)
        # cv2.line(image, (0, 0), (img_ctr_x, img_ctr_y), (255,0,0), 5)
    except Exception as e:
        # print(e)
        pass
    # image = cv2.flip(image, 1)
    # cv2.imshow('frame', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    print(img_ctr_x, img_ctr_y, (time_ns() - start)*1e-9)
# After the loop release the cap object
# vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

"""
frame = np.array(Image.open(fp="raspberry/controllers/tape.png")) 
print(frame.shape)

fig, sub_plts = plt.subplots(2, 3)

z_frame = np.zeros(frame.shape, dtype="uint8")
z_frame[:, :, 0] = frame[:, :, 0]*((frame[:, :, 0] < 80) * (frame[:, :, 1] < 60) * (frame[:, :, 2] < 80))
# z_frame[:, :, 0] = (frame[:, :, 0] + frame[:, :, 1] + frame[:, :, 2])//3
sub_plts[0, 0].imshow(z_frame)
z_frame[:, :, 0] = frame[:, :, 0]
sub_plts[1, 0].imshow(z_frame)

z_frame = np.zeros(frame.shape, dtype="uint8")
z_frame[:, :, 1] = frame[:, :, 1]*(frame[:, :, 1] > 80)
sub_plts[0, 1].imshow(z_frame)
z_frame[:, :, 1] = frame[:, :, 1]
sub_plts[1, 1].imshow(z_frame)

z_frame = np.zeros(frame.shape, dtype="uint8")
z_frame[:, :, 2] = frame[:, :, 2]*(frame[:, :, 2] > 80)
sub_plts[0, 2].imshow(z_frame)
z_frame[:, :, 2] = frame[:, :, 2]
sub_plts[1, 2].imshow(z_frame)


plt.show()
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
# After the loop release the cap object
# vid.release()
# Destroy all the windows
cv2.destroyAllWindows()"""