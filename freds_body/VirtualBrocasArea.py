from openai import OpenAI
from queue import Queue, Empty
import threading
import sys
import json
import requests
from freds_body import BrocasArea

class VirtualBrocasArea(BrocasArea):
    def init_engine(self):
        self.openai = OpenAI()

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
                print(f"Error generating response: {e}")

    