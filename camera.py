import cv2
import numpy as np

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(1)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()

        # Convert the frame from BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the range of red color in HSV
        low_red = np.array([0, 120, 70])
        high_red = np.array([10, 255, 255])

        # Create a mask for the red color
        red_mask = cv2.inRange(hsv, low_red, high_red)

        # Bitwise-AND mask and original image
        red = cv2.bitwise_and(frame, frame, mask=red_mask)

        # Find contours in the red mask
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw the largest contour on the original frame
        if len(contours) > 0:
            contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(contour)
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            # Calculate the distance from the center of the red circle to the edges of the frame
            distance_left = cx
            distance_right = frame.shape[1] - cx
            distance_top = cy
            distance_bottom = frame.shape[0] - cy

            # Draw labels with the distances on the frame
            cv2.putText(frame, f"Left: {distance_left}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Right: {distance_right}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Top: {distance_top}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Bottom: {distance_bottom}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Stack the original frame and the red mask horizontally
        result = np.hstack((frame, red))

        # Convert the result to JPEG format
        ret, jpeg = cv2.imencode('.jpg', result)

        # Return the JPEG bytes
        return jpeg.tobytes()