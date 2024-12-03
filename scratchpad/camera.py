from picamzero import Camera

cam = Camera()
cam.start_preview()
cam.capture_sequence("sequence.jpg", num_images=3, interval=2)
cam.stop_preview()