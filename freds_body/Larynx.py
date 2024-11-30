import threading
from queue import Queue
import sherpa_onnx
import simpleaudio as sa
import numpy as np

SAMPLING_RATE = 16000

class Larynx:
    def __init__(self):
        self.response_queue = Queue()
        self.tts_thread = threading.Thread(target=self._convert_to_speech)
        self.tts_thread.daemon = True
        self.stop_event = threading.Event()

        tts_config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model="models/vits-piper-en_US-amy-medium/en_US-amy-medium.onnx",
                    lexicon="",
                    tokens="models/vits-piper-en_US-amy-medium/tokens.txt",
                    data_dir="models/vits-piper-en_US-amy-medium/espeak-ng-data"
                ),
            ),
            max_num_sentences=10,
        )

        self.tts = sherpa_onnx.OfflineTts(tts_config)

    def start(self):
        self.tts_thread.start()

    def stop(self):
        self.stop_event.set()
        self.tts_thread.join()

    def _convert_to_speech(self):
        while not self.stop_event.is_set():
            try:
                response = self.response_queue.get(timeout=1)
            except Exception:
                continue

            # Convert text to speech using Sherpa-ONNX TTS
            if response:
                audio = self.tts.generate(response)
                self._play_audio(audio)

    def _play_audio(self, audio):
        # Normalize audio to int16 range
        #audio_int16 = np.int16(audio.samples * 32767)
        play_obj = sa.play_buffer(np.array(audio.samples), 1, 2, audio.sample_rate)
        play_obj.wait_done()

    def add_response(self, response):
        self.response_queue.put(response)