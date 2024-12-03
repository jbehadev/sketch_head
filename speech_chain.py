import threading
import time
import requests
from freds_body import WernickesArea, VirtualBrocasArea, Larynx, VirtualLarynx

thalamus_url = 'http://localhost:8000'

def done_talking():
    event = []
    event.append('L')
    event.append(40)
    event.extend([255,255,255])
    event.append('|')
    event.append('R')
    event.append(40)
    event.extend([255,255,255])
    event.append('|')
    event.append('D')
    event.append(ascii(10))
    event.append('|')
    event.append('E')
    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})

def bag_trick():
    event = []
    event.append('L')
    event.append(100)
    event.extend([255,0,0])
    event.append('|')
    event.append('R')
    event.append(100)
    event.extend([255,0,0])
    event.append('|')
    event.append('D')
    event.append(ascii(30))
    event.append('|')
    event.append('T')
    event.append(ascii(90))
    event.append('|')
    event.append('S')
    event.append(ascii(10))
    event.append('|')
    event.append('E')

    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})
    event = []
    event.append('D')
    event.append(ascii(50))
    event.append('|')
    event.append('S')
    event.append(ascii(180))
    event.append('|')
    event.append('E')
    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})
    event = []
    event.append('D')
    event.append(ascii(50))
    event.append('|')
    event.append('S')
    event.append(ascii(10))
    event.append('|')
    event.append('E')
    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})
    event = []
    event.append('D')
    event.append(ascii(50))
    event.append('|')
    event.append('S')
    event.append(ascii(180))
    event.append('|')
    event.append('E')
    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})

def ignore_talking_wrapper(response):
    listener.pause = True
    print('Shutting off hearing')
    talker.is_busy = True
    talker.add_response(response)
    while talker.is_busy:
        pass
    listener.pause = False
    print('Turning on hearing')

# Example usage:
listener = WernickesArea(model_name="moonshine/base")
listener.start_listening()
responder = VirtualBrocasArea(thalamus_url=thalamus_url)
responder.start()
talker = VirtualLarynx()
talker.start()
while True:
    transcription = listener.get_transcription()
    if transcription:
        print("Transcription:", transcription)
        if all(x in transcription for x in ["get", "in", "the", "bag"]):
            ignore_talking_wrapper("No![pause] No![pause] No![pause] No!")
            bag_trick()
            continue
        responder.add_transcription(transcription)
    response = responder.get_response()
    if response:
       print("Response:", response)
       ignore_talking_wrapper(response)
       done_talking()

       
        