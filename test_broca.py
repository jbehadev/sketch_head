import threading
import time

from freds_body import VirtualBrocasArea, Larynx

thalamus_url = 'http://localhost:8000'

# Example usage:
responder = VirtualBrocasArea(thalamus_url=thalamus_url)
responder.start()

talker = Larynx()
talker.start()

responder.add_transcription("Tell me a joke.")
while True:
    response = responder.get_response()
    if response:
        print("Response:", response)
        talker.add_response(response)
        time.sleep(30)
        responder.add_transcription("Tell me a sad story")

