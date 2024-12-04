import cv2
import threading
import requests
from picamera2 import Picamera2
import time
from loguru import logger

class Eyes(threading.Thread):
    def __init__(self, thalamus_url):
        super(Eyes, self).__init__()
        self.thalamus_url = thalamus_url
        self.stop_event = threading.Event()

        # Servo control ranges
        self.SWIVEL_MIN, self.SWIVEL_MAX = 1, 180
        self.TILT_MIN, self.TILT_MAX = 1, 120

        # Initial servo positions
        self.swivel_position = (self.SWIVEL_MIN + self.SWIVEL_MAX) // 2
        self.tilt_position = (self.TILT_MIN + self.TILT_MAX) // 2

        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Initialize Picamera2
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
        self.camera.start()
        self.tracking_on = False

    def map_to_range(self, value, in_min, in_max, out_min, out_max):
        """Map a value from one range to another."""
        return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def run(self):
        while not self.stop_event.is_set():
            # Capture frame from Picamera2
            frame = self.camera.capture_array()

            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                # Use the first detected face
                (x, y, w, h) = faces[0]

                # Calculate the center of the face
                face_center_x = x + w // 2
                face_center_y = y + h // 2

                # Calculate offsets from the center of the frame
                offset_x = face_center_x - 640 / 2  # Frame width = 640
                offset_y = face_center_y - 480 / 2  # Frame height = 480

                # Map offsets to servo positions
                self.swivel_position = self.map_to_range(offset_x, -320, 320, 180, 5)
                self.tilt_position = self.map_to_range(offset_y, -240, 240, -10, 150)

                # Clamp the values to servo ranges
                self.swivel_position = max(self.SWIVEL_MIN, min(self.SWIVEL_MAX, self.swivel_position))
                self.tilt_position = max(self.TILT_MIN, min(self.TILT_MAX, self.tilt_position))

                # Create event for head movement
                # Create event for head movement

                event = [
                    'L', int(90), int(0), int(0), int(255), '|',
                    'R', int(90), int(0), int(0), int(255), '|',
                    'S', ascii(self.swivel_position), '|',
                    'T', ascii(self.tilt_position), '|',
                    'D', ascii(40), '|',  # Adjust duration as needed
                    'E'
                ]

                if self.tracking_on:
                    logger.info('{file} found a face at {offset_x}, {offset_y}', file=__file__, offset_x=offset_x, offset_y=offset_y)
                    response = requests.post(f'{self.thalamus_url}/play_event', json={'event': event})

            # Display the video feed with face tracking (optional)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        self.camera.stop()
        cv2.destroyAllWindows()

    def stop(self):
        """Signal the thread to stop."""
        self.stop_event.set()
