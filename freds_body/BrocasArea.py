from queue import Queue, Empty
import json
import threading
import os
import math
import random
from llama_cpp import Llama
import requests
from loguru import logger

class BrocasArea:
    def __init__(self, thalamus_url):
        self.thalamus_url = thalamus_url
        self.transcription_queue = Queue()
        self.response_queue = Queue()
        self.response_thread = threading.Thread(target=self._generate_response)
        self.response_thread.daemon = True
        self.stop_event = threading.Event()
        self.context = []

        self.init_engine()

    def init_engine(self):
        
        self.model = Llama(
            model_path="models/phi-2.Q4_0.gguf",
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

    def wrapper(self, statement):
        return f"Please return an emotion like EMOTION: [emotion] then the response to this query: {statement}\nOutput:"
    
    def template(self, statement):
            return [
                {"role": "system", "content": "When responding, please respond with EMOTION: {emotion of response}\n response to the query"},
                {
                    "role": "user",
                    "content": statement
                }
            ]

    def _generate_response(self):
        while not self.stop_event.is_set():
            try:
                transcription = self.transcription_queue.get(timeout=1)
            except Empty:
                continue
            
            logger.info('{file} Brocas is thinking', file=__file__)
            
            llm_response = ""
            for token in self.model(self.wrapper(transcription), stream=True):
                llm_response += token['choices'][0]['text']
            #llm_response =  self.model.create_chat_completion(
                #messages = self.template(transcription)
            #)

            # Put the response in the response queue
            self.response_queue.put(llm_response)

    def add_transcription(self, transcription):
        self.transcription_queue.put(transcription)

    def get_response(self):
        try:
            return self.response_queue.get_nowait()
        except Empty:
            return None

    def make_movement(self, json_data, conversation_length):
        for i in range(0,math.ceil(conversation_length/10)):
            event = []
            # Left eye settings (assuming the same for both eyes for simplicity)
            if "eye_settings" in json_data and "color" in json_data["eye_settings"] and "rgb" in json_data["eye_settings"]["color"]:
                left_rgb = json_data["eye_settings"]["color"]["rgb"]
                left_brightness = json_data["eye_settings"].get("brightness", 50)  # Default to 50% if not provided
                left_brightness = min(100,left_brightness + random.randint(-20,20))
                event.append('L')
                event.append(left_brightness)
                event.append(left_rgb["red"])
                event.append(left_rgb["green"])
                event.append(left_rgb["blue"])
                event.append('|')
                
                # Assuming the same settings for the right eye (can be adjusted if right settings differ)
                right_rgb = json_data["eye_settings"]["color"]["rgb"]
                right_brightness = json_data["eye_settings"].get("brightness", 50)  # Default to 50% if not provided
                right_brightness = min(100,right_brightness + random.randint(-20,20))
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
                tilt_angle = min(max(tilt_angle + random.randint(-20,20),20),160)
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
                swivel_angle = min(max(swivel_angle + random.randint(-20,20),20),180)
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
                event.append(ascii(40))
                event.append('|')
            
            # End of event
            event.append('E')
            
            response = requests.post(f'{self.thalamus_url}/play_event', json={'event': event})