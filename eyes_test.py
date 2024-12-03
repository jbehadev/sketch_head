import threading
import time

from freds_body import VirtualBrocasArea, Larynx, Eyes

thalamus_url = 'http://localhost:8000'

# Example usage:
vision = Eyes(thalamus_url=thalamus_url)
vision.start()

try:
    while True:
         pass
except KeyboardInterrupt:
        print("Stopping face tracker...")
        vision.stop()
        vision.join()

