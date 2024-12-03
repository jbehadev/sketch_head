import threading
import time

from freds_body import BrocasArea, Larynx

thalamus_url = 'http://localhost:8000'

# Example usage:
responder = BrocasArea(thalamus_url=thalamus_url)
responder.start()

talker = Larynx()
talker.start()
start_time = time.time()
responder.add_transcription("Tell me a joke.")
while True:
    response = responder.get_response()
    if response:
        print("Response:", response)
        print(f"Response took {round(time.time()-start_time,2)} seconds")
        start_time = time.time()
        responder.add_transcription("Tell me a sad story")

