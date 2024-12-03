import threading
import time

from freds_body import WernickesArea, VirtualBrocasArea, Larynx

thalamus_url = 'http://localhost:8000'

# Example usage:
listener = WernickesArea(model_name="moonshine/base")
listener.start_listening()
responder = VirtualBrocasArea(thalamus_url=thalamus_url)
responder.start()
talker = Larynx()
talker.start()
while True:
    transcription = listener.get_transcription()
    if transcription:
        print("Transcription:", transcription)
        responder.add_transcription(transcription)
    response = responder.get_response()
    if response:
       print("Response:", response)
       talker.add_response(response)