import threading
import time

from freds_body import BrocasArea, Larynx
# Example usage:
responder = BrocasArea()
responder.start()
responder.add_transcription("Fred tell me a joke")
while True:
    response = responder.get_response()
    if response:
        print("Response:", response)
        responder.add_transcription("Fred tell me another joke")
