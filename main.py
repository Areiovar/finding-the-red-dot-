from flask import Flask, render_template, Response, jsonify
from camera import VideoCamera
from serial.tools import list_ports
import pydobot
import cv2
import numpy as np

app = Flask(name)
available_ports = list_ports.comports()
print(f"available ports: {[x.device for x in available_ports]}")
COMPort = available_ports[0].device


class VideoCamera:
    def init(self):
        self.video = cv2.VideoCapture(0)
        self.x1 = 0
        self.y1 = 0
        self.cx = 0
        self.cy = 0

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

        contours, _ = cv2.findContours(
            red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(contour)
            self.cx, self.cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            cv2.circle(frame, (self.cx, self.cy), 5, (0, 0, 255), -1)
            to_dot_x = ""
            to_dot_y = ""
            device = pydobot.Dobot(port=COMPort, verbose=False)
            x, y, z, r, j1, j2, j3, j4 = device.pose()

            self.x1, self.y1 = center_x - self.cx, center_y - self.cy
            if self.x1 < 0:
                to_dot_x = "Left"
            else:
                to_dot_x = "Right"
            if self.y1 < 0:
                to_dot_y = "Up"
            else:
                to_dot_y = "Down"
            if self.x1 == 0 and self.y1 == 0:
                to_dot_x, to_dot_y = "True", "True"
            if self.x1 == 0:
                to_dot_x = "equal"
            if self.y1 == 0:
                to_dot_y = "equal"
            print(self.x1)
            while self.cx != center_x:
                contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(contour)
                self.cx, self.cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                if self.cx < center_x:
                    device.move_to(x, y + 10, z, r, wait=False)
                elif self.cx > center_x:
                    device.move_to(x, y - 10, z, r, wait=False)

                if self.x1 > 20 or self.x1 < 20:
                    break
                x, y, z, r, j1, j2, j3, j4 = device.pose()
                self.x1 = abs(center_x - self.cx)
            cv2.putText(
                frame,
                f"to dot x1: {to_dot_x} and y1: {to_dot_y}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            cv2.putText(
                frame,
                f"red dot: {self.cx} {self.cy}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            result = np.hstack((frame, red))
            self.distance = int(
                np.sqrt((self.cx - center_x)  2 + (self.cy - center_y)  2)
            )

            ret, jpeg = cv2.imencode(".jpg", result)
            return jpeg.tobytes()

    def get_coords(self):
        return self.x1, self.y1


video_stream = VideoCamera()
red_video_stream = VideoCamera()


@app.route("/")
def index():
    return render_template("index.html")


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/video_feed")
def video_feed():
    def gen():
        while True:
            frame = video_stream.get_frame()
