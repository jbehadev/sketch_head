import threading
import time
import requests
from freds_body import WernickesArea, VirtualBrocasArea, VirtualLarynx, Eyes
from loguru import logger
logger.add('freds_inner_monolog.log', level="INFO")
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
    event.append(ascii(60))
    event.append('|')
    event.append('E')

    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})
    event = []
    event.append('D')
    event.append(ascii(50))
    event.append('|')
    event.append('S')
    event.append(ascii(120))
    event.append('|')
    event.append('E')
    ignore_talking_wrapper("No![pause] No![pause] No![pause] No!")

    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})
    event = []
    event.append('D')
    event.append(ascii(50))
    event.append('|')
    event.append('S')
    event.append(ascii(60))
    event.append('|')
    event.append('E')
    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})
    event = []
    event.append('D')
    event.append(ascii(50))
    event.append('|')
    event.append('S')
    event.append(ascii(120))
    event.append('|')
    event.append('E')
    response = requests.post(f'{thalamus_url}/play_event', json={'event': event})

def ignore_talking_wrapper(response):
    listener.pause = True
    logger.info('{file} Shutting off hearing', file=__file__)
    talker.is_busy = True
    talker.add_response(response)
    while talker.is_busy:
        pass
    listener.pause = False
    logger.info('{file} Turning on hearing', file=__file__)

# Example usage:
listener = WernickesArea(model_name="moonshine/base")
listener.start_listening()
responder = VirtualBrocasArea(thalamus_url=thalamus_url)
responder.start()
talker = VirtualLarynx()
talker.start()
vision = Eyes(thalamus_url=thalamus_url)
vision.start()
ignore_talking_wrapper('Welcome all! I have a brain now.')
while True:
    transcription = listener.get_transcription()
    if transcription:
        logger.info('{file} Transcription: {transcription}', file=__file__, transcription=transcription)
        if all(x in transcription for x in ["get", "in", "the", "bag"]):
            bag_trick()
            continue
        elif all(x in transcription for x in ["creep", "mode", "on"]):
            ignore_talking_wrapper("I see you!")
            vision.tracking_on = True 
            continue   
        elif all(x in transcription for x in ["creep", "mode", "off"]):
            ignore_talking_wrapper("Where did you go?")
            vision.tracking_on = False 
            continue 
        responder.add_transcription(transcription)
    response = responder.get_response()
    if response:
        logger.info('{file} Response: {response}', file=__file__, response=response)
        ignore_talking_wrapper(response)
        done_talking()

       
        