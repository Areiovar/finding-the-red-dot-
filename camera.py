import cv2
import numpy as np
from serial.tools import list_ports
import pydobot
#
#
# available_ports = list_ports.comports()
# print(f'available ports: {[x.device for x in available_ports]}')
# port = available_ports[0].device
#
# device = pydobot.Dobot(port=port, verbose=True)
# (x, y, z, r, j1, j2, j3, j4) = device.pose()
# device.move_to(x, y, z, r, wait=False)

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(1)


    def get_frame(self):

        ret, frame = self.video.read()

        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2

        cv2.circle(frame, (center_x, center_y), 5, (255, 255, 255), -1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        low_red = np.array([0, 120, 70])
        high_red = np.array([10, 255, 255])

        red_mask = cv2.inRange(hsv, low_red, high_red)

        red = cv2.bitwise_and(frame, frame, mask=red_mask)

        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(contour)
        cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        to_dot_x = ""
        to_dot_y = ""
        distance_left = cx
        distance_right = frame.shape[1] - cx
        distance_top = cy
        distance_bottom = frame.shape[0] - cy

        x1, y1 = center_x - cx, center_y - cy
        if x1 < 0:
            to_dot_x = "Left"
        else:
            to_dot_x = "Right"
        if y1 < 0:
            to_dot_y = "Up"
        else:
            to_dot_y = "Down"
        if x1 == 0 and y1 == 0:
            to_dot_x, to_dot_y = 'True', 'True'
        if x1 == 0:
            to_dot_x = 'equel'
        if y1 == 0:
            to_dot_y = 'equel'

        cv2.putText(frame, f"to dot x1: {to_dot_x} and y1: {to_dot_y}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 2)
        print(x1, y1)
        result = np.hstack((frame, red))
        self.distance = int(np.sqrt((cx - center_x) ** 2 + (cy - center_y) ** 2))

        ret, jpeg = cv2.imencode('.jpg', result)
        return jpeg.tobytes()
