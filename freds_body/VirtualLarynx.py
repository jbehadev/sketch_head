import threading
from queue import Queue, Empty
from openai import OpenAI
import numpy as np
import os
import wave
from io import BytesIO
import tempfile
import simpleaudio as sa
from loguru import logger

SAMPLING_RATE = 16000

class VirtualLarynx:
    def __init__(self):
        self.response_queue = Queue()
        self.tts_thread = threading.Thread(target=self._convert_to_speech)
        self.tts_thread.daemon = True
        self.stop_event = threading.Event()
        self.is_busy = False

        self.tts = OpenAI()

    def start(self):
        self.tts_thread.start()

    def stop(self):
        self.stop_event.set()
        self.tts_thread.join()

    def _convert_to_speech(self):
        while not self.stop_event.is_set():
            try:
                response = self.response_queue.get(timeout=1)
            except Empty:
                continue
            self.is_busy = True
            response =  self.tts.audio.speech.create(
                    model="tts-1",
                    voice="fable",
                    input=response,
                    response_format="wav"
            ) 
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_path = temp_audio_file.name
                response.stream_to_file(temp_audio_path)
            # Play the WAV file
            try:
                # Open the WAV file
                with wave.open(temp_audio_path, "rb") as wav_file:
                    # Extract WAV parameters
                    num_channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    frame_rate = wav_file.getframerate()
                    pcm_data = wav_file.readframes(wav_file.getnframes())
                    # Play the audio using simpleaudio
                    play_obj = sa.play_buffer(pcm_data, num_channels, sample_width, frame_rate)
                    play_obj.wait_done()
            except Exception as e:
                logger.info("{file} Error generating response: {e}", file=__file__, e=e)
            finally:
                # Clean up the temporary file
                os.remove(temp_audio_path)
                self.is_busy = False

        
    def add_response(self, response):
        self.response_queue.put(response)