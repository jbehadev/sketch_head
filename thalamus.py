# event_manager.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union
import argparse
import serial
import sys
import uvicorn

arg_parse = argparse.ArgumentParser(add_help=False)
arg_parse.add_argument('--env', required=True)

arguments, unknown = arg_parse.parse_known_args()

app = FastAPI()

# Define your serial connection (replace with your actual configuration)
class ArduinoMock:
    def readline(self):
        return b""
    
    def write(self, output):
        print(output)

if(arguments.env == 'prod'):
    arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
else:
    arduino = ArduinoMock()

# Event storage
saved_events = []

# Pydantic models for request bodies
class Event(BaseModel):
    event: List[Union[int, str]]

class SavedEvent(BaseModel):
    name: str
    event: List[Union[int, str]]

@app.post('/play_event')
def play_event(event: Event):

    if type(event.event) == list:
        write_list(event.event)
    else:
        write_list([*event.event])
    
    while True:
        line = arduino.readline()
        if line == b'':
            break
        else:
            print(line.decode().strip('\r\n'))

    return {'status': 'played'}

@app.post('/save_event')
def save_event(saved_event: SavedEvent):
    saved_events.append({'name': saved_event.name, 'event': saved_event.event})
    return {'status': 'saved'}

@app.get('/saved_events')
def get_saved_events():
    return {'saved_events': saved_events}

@app.post('/clear_events')
def clear_events():
    saved_events.clear()
    return {'status': 'cleared'}

def write_read(x):
    if type(x) == int:
        arduino.write(x.to_bytes(1, 'little'))
        print(x.to_bytes(1, 'little'))
    else:
        arduino.write(bytes(x, 'utf-8'))
        print(bytes(x, 'utf-8'))

def write_list(event_list):
    [write_read(ev) for ev in event_list]

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
