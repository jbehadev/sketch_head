import cv2
import mediapipe as mp
import numpy as np
from picamera2 import Picamera2
import time

# Initialize MediaPipe Face Mesh and drawing utilities
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize the Picamera2
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

time.sleep(2)  # Allow the camera to warm up

# Get frame dimensions
frame_width = 640
frame_height = 480

# Camera internals (assuming no lens distortion)
focal_length = frame_width
center = (frame_width / 2, frame_height / 2)
camera_matrix = np.array(
    [[focal_length, 0, center[0]],
     [0, focal_length, center[1]],
     [0, 0, 1]], dtype="double")
dist_coeffs = np.zeros((4, 1))

# Set up the video writer to save to MP4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

# Main loop for real-time processing
try:
    while True:
        # Capture frame from Picamera2
        frame = picam2.capture_array()

        # Flip the frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # The frame is in RGB format
        rgb_frame = frame

        # Process the frame to detect facial landmarks
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            # Use the first detected face
            face_landmarks = results.multi_face_landmarks[0]

            # Define landmark indices for head pose estimation
            landmark_ids = [1, 152, 33, 263, 61, 291]

            # Collect corresponding 2D image points
            image_points = []
            for idx in landmark_ids:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                image_points.append((x, y))

            image_points = np.array(image_points, dtype='double')

            # Define 3D model points of facial landmarks
            model_points = np.array([
                (0.0, 0.0, 0.0),             # Nose tip
                (0.0, -330.0, -65.0),        # Chin
                (-225.0, 170.0, -135.0),     # Left eye left corner
                (225.0, 170.0, -135.0),      # Right eye right corner
                (-150.0, -150.0, -125.0),    # Left mouth corner
                (150.0, -150.0, -125.0)      # Right mouth corner
            ])

            # SolvePnP to estimate head pose
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

            # Project a 3D point (e.g., a point extending from the nose tip)
            (nose_end_point2D, _) = cv2.projectPoints(
                np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)

            # Convert the frame to BGR for OpenCV visualization
            frame_bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

            # Draw the landmarks and the head pose line
            for point in image_points:
                cv2.circle(frame_bgr, (int(point[0]), int(point[1])), 3, (0, 0, 255), -1)

            p1 = (int(image_points[0][0]), int(image_points[0][1]))
            p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
            cv2.line(frame_bgr, p1, p2, (255, 0, 0), 2)

            # Optionally, draw the face mesh
            mp_drawing.draw_landmarks(
                frame_bgr,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )

        else:
            # If no face is detected, convert the frame for saving
            frame_bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        # Write the frame to the video file
        out.write(frame_bgr)

except KeyboardInterrupt:
    pass

finally:
    # Release resources
    picam2.close()
    out.release()
    cv2.destroyAllWindows()
