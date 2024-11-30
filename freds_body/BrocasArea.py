from queue import Queue, Empty
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import threading
import os
from llama_cpp import Llama

class BrocasArea:
    def __init__(self):
        self.transcription_queue = Queue()
        self.response_queue = Queue()
        self.response_thread = threading.Thread(target=self._generate_response)
        self.response_thread.daemon = True
        self.stop_event = threading.Event()

        self.model = Llama(
            model_path="models/phi-2.Q8_0.gguf",
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
            stop=None,
            n_ctx=2048
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
            llm_response = ""
            #llm_response = self.model(transcription)
            for token in self.model(transcription, max_tokens=2048, stream=True):
                llm_response += token['choices'][0]['text']

            # Put the response in the response queue
            self.response_queue.put(llm_response)

    def add_transcription(self, transcription):
        self.transcription_queue.put(transcription)

    def get_response(self):
        try:
            return self.response_queue.get_nowait()
        except Empty:
            return None