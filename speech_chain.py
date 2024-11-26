import threading
import time

from freds_body import WernickesArea, BrocasArea, Larynx
# Example usage:
listener = WernickesArea(model_name="moonshine/base")
listener.start_listening()
responder = BrocasArea()
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