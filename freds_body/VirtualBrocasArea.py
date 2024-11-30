from openai import OpenAI
from queue import Queue, Empty
import threading
import sys
import json

class VirtualBrocasArea:
    def __init__(self):
        self.transcription_queue = Queue()
        self.response_queue = Queue()
        self.response_thread = threading.Thread(target=self._generate_response)
        self.response_thread.daemon = True
        self.stop_event = threading.Event()
        self.openai = OpenAI()
        self.context = []
        self.context.append({
            'role': 'system',
            "content": [
                {
                    "type": "text",
                    "text": "You are a robotic assistant managing a robotic head that is named Fred. The head can tilt up and down, turn left and right, and the eyes can change color and brightness. \n\nWhen responding, provide instructions in only JSON format for what the head coordinates and eye color/brightness should be before the response and what head coordinates and eye/color brightness should be after the response to the query. Follow the format in the example below:\n\nExample JSON:\n{\n  \"before\": {\n      \"head_movement\": {\n        \"tilt\": {\n          \"angle\": 10,\n          \"direction\": \"up\"\n        },\n        \"turn\": {\n          \"angle\": 15,\n          \"direction\": \"right\"\n        }\n      },\n      \"eye_settings\": {\n        \"color\": {\n          \"shade\": \"blue\",\n          \"brightness\": 50\n        }\n      }\n  },\n  \"after\": {\n    \"head_movement\": {\n      \"tilt\": {\n        \"angle\": 20,\n        \"direction\": \"up\"\n      },\n      \"turn\": {\n        \"angle\": 5,\n        \"direction\": \"right\"\n      }\n    },\n    \"eye_settings\": {\n      \"color\": {\n        \"shade\": \"brown\",\n        \"brightness\": 20\n      }\n    }\n  },\n\"response\": {response}\n}\n"
                }
            ]
        })

    def start(self):
        self.response_thread.start()

    def stop(self):
        self.stop_event.set()
        self.response_thread.join()

    def _generate_response(self):
        while not self.stop_event.is_set():
            try:
                transcription = self.transcription_queue.get(timeout=1)
            except Exception:
                continue

            # Generate response using OpenAI API
            try:
                self.context.append({
                    'role': 'user',
                    "content": [
                        {
                            "type": "text",
                            "text": transcription
                        }
                    ]
                })
                response = self.openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.context,
                    response_format={
                        "type": "json_object"
                    },
                    temperature=1,
                    max_tokens=2048,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                response = json.loads(response.choices[0].message.to_dict()['content'])
                movement_before = response['before']
                movement_after = response['after']
                message = response['response']

                self.context.append({
                    'role': 'assistant',
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                })

                self.response_queue.put(message)
            except Exception as e:
                print(f"Error generating response: {e}")

    def add_transcription(self, transcription):
        self.transcription_queue.put(transcription)

    def get_response(self):
        try:
            return self.response_queue.get_nowait()
        except Empty:
            return None