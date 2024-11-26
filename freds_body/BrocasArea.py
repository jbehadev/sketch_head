from queue import Queue, Empty
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import threading
import os


class BrocasArea:
    def __init__(self):
        self.transcription_queue = Queue()
        self.response_queue = Queue()
        self.response_thread = threading.Thread(target=self._generate_response)
        self.response_thread.daemon = True
        self.stop_event = threading.Event()

        # Load DialoGPT small model
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", token=os.environ.get('HFACE_TOKEN'))
        self.model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", token=os.environ.get('HFACE_TOKEN'))

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
            # Generate response using DialoGPT
            input_ids = self.tokenizer.encode(transcription + self.tokenizer.eos_token, return_tensors="pt")
            with torch.no_grad():
                print('Brocas is thinking')

                output = self.model.generate(input_ids, max_length=50, pad_token_id=self.tokenizer.eos_token_id)
            response = self.tokenizer.decode(output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

            # Put the response in the response queue
            self.response_queue.put(response)

    def add_transcription(self, transcription):
        self.transcription_queue.put(transcription)

    def get_response(self):
        try:
            return self.response_queue.get_nowait()
        except Empty:
            return None