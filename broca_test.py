import threading
import time

from freds_body import BrocasArea, Larynx
# Example usage:
responder = BrocasArea()
responder.start()

def wrap_response(text):
    prompt = """
Provide the emotion of your response in the following format: EMOTION: {emotion}. Then, include your response.

For example:
Query: "How are you?"
Response: EMOTION: Happy

Now respond to this query: 
"""
    return prompt + text

talker = Larynx()
talker.start()

responder.add_transcription(wrap_response("Tell me a joke."))
while True:
    response = responder.get_response()
    if response:
        print("Response:", response)
        talker.add_response(response)
        responder.add_transcription(wrap_response("Tell me a sad story"))

