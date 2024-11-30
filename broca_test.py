import threading
import time

from freds_body import VirtualBrocasArea, Larynx
# Example usage:
responder = VirtualBrocasArea()
responder.start()

talker = Larynx()
talker.start()

responder.add_transcription("Tell me a joke.")
while True:
    response = responder.get_response()
    if response:
        print("Response:", response)
        talker.add_response(response)
        responder.add_transcription("Tell me a sad story")

