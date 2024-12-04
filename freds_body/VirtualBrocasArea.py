from openai import OpenAI
from queue import Queue, Empty
import threading
import sys
import json
import requests
from freds_body import BrocasArea
from loguru import logger

class VirtualBrocasArea(BrocasArea):
    def init_engine(self):
        self.openai = OpenAI()
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
                "angle": 50,  // 5 to 180 degrees, 5 is to the right and 180 is to the left
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
                actions = response['actions']
                self.make_movement(actions)
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
                logger.info("{file} Error generating response: {e}", file=__file__, e=e)

    