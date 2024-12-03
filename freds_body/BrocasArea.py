from queue import Queue, Empty
import json
import threading
import os
from llama_cpp import Llama
import requests

class BrocasArea:
    def __init__(self, thalamus_url):
        self.thalamus_url = thalamus_url
        self.transcription_queue = Queue()
        self.response_queue = Queue()
        self.response_thread = threading.Thread(target=self._generate_response)
        self.response_thread.daemon = True
        self.stop_event = threading.Event()
        self.context = []
        self.context.append({
            'role': 'system',
            "content": [
                {
                    "type": "text",
                    "text": """You are a robotic assistant managing a robotic head that is named Fred. The head can tilt up and down, turn left and right, and the eyes can change color and brightness. 

When responding, provide instructions in only JSON format for what the head coordinates and eye color/brightness should be before the response and what head coordinates and eye/color brightness should be after the response to the query. Follow the format in the example below:

Example JSON:
{
    "actions": {
        "head_movement": {
            "tilt": {
                "angle": 90,  // 5 to 120 degrees, 5 being up and 120 being down
            },
            "swivel": {
                "angle": 50,  // 5 to 180 degrees, 5 is to the left and 180 is to the right
            },
            "duration": 100  // 50 to 200 cycles
        },
        "eye_settings": {
            "color": {
            "rgb": {
                "red": 0,  // 0 to 255
                "green": 128,  // 0 to 255
                "blue": 255  // 0 to 255
            },
            "brightness": 50  // Percentage (0 to 100)
            }
        }
    },
    "response": {response}
}"""
                }
            ]
        })
        self.init_engine()

    def init_engine(self):
        
        self.model = Llama(
            model_path="models/phi-2.Q8_0.gguf",
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
            stop=None,
            n_ctx=2048,
            verbose=False
        )

    def start(self):
        self.response_thread.start()

    def stop(self):
        self.stop_event.set()
        self.response_thread.join()

    def _generate_response(self):
        while not self.stop_event.is_set():
            try:
                transcription = self.transcription_queue.get(timeout=1)
            except Empty:
                continue
            
            print('Brocas is thinking')
            self.context.append({
                'role': 'user',
                "content": [
                    {
                        "type": "text",
                        "text": transcription
                    }
                ]
            })
            llm_response = ""
            #llm_response = self.model(transcription)
            for token in self.model(json.dumps(self.context), max_tokens=2048, stream=True):
                llm_response += token['choices'][0]['text']

            self.context.append({
                'role': 'assistant',
                "content": [
                    {
                        "type": "text",
                        "text": llm_response
                    }
                ]
            })

            # Put the response in the response queue
            self.response_queue.put(llm_response)
            print(llm_response)

    def add_transcription(self, transcription):
        self.transcription_queue.put(transcription)

    def get_response(self):
        try:
            return self.response_queue.get_nowait()
        except Empty:
            return None

    def make_movement(self, json_data):
        event = []
        print(json_data)
        # Left eye settings (assuming the same for both eyes for simplicity)
        if "eye_settings" in json_data and "color" in json_data["eye_settings"] and "rgb" in json_data["eye_settings"]["color"]:
            left_rgb = json_data["eye_settings"]["color"]["rgb"]
            left_brightness = json_data["eye_settings"].get("brightness", 50)  # Default to 50% if not provided
            event.append('L')
            event.append(left_brightness)
            event.append(left_rgb["red"])
            event.append(left_rgb["green"])
            event.append(left_rgb["blue"])
            event.append('|')
            
            # Assuming the same settings for the right eye (can be adjusted if right settings differ)
            right_rgb = json_data["eye_settings"]["color"]["rgb"]
            right_brightness = json_data["eye_settings"].get("brightness", 50)  # Default to 50% if not provided
            event.append('R')
            event.append(right_brightness)
            event.append(right_rgb["red"])
            event.append(right_rgb["green"])
            event.append(right_rgb["blue"])
            event.append('|')
        else:
            event.append('L')
            event.append(0)
            event.extend([0,0,0])
            event.append('|')
            event.append('R')
            event.append(0)
            event.extend([0,0,0])
            event.append('|')
        
        # Tilt settings
        if "head_movement" in json_data and "tilt" in json_data["head_movement"]:
            tilt_angle = json_data["head_movement"]["tilt"]["angle"]
            event.append('T')
            event.append(ascii(tilt_angle))
            event.append('|')
        else:
            event.append('T')
            event.append(ascii(90))
            event.append('|')
        
        # Swivel settings
        if "head_movement" in json_data and "swivel" in json_data["head_movement"]:
            swivel_angle = json_data["head_movement"]["swivel"]["angle"]
            event.append('S')
            event.append(ascii(swivel_angle))
            event.append('|')
        else:
            event.append('S')
            event.append(ascii(90))
            event.append('|')
        
        # Duration
        if "head_movement" in json_data and "duration" in json_data["head_movement"]:
            duration = json_data["head_movement"]["duration"]
            event.append('D')
            event.append(ascii(duration))
            event.append('|')
        else:
            event.append('D')
            event.append(ascii(0))
            event.append('|')
        
        # End of event
        event.append('E')
        
        response = requests.post(f'{self.thalamus_url}/play_event', json={'event': event})