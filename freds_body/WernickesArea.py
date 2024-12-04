import threading
import time
import numpy as np
from queue import Queue, Empty
from sounddevice import InputStream
from silero_vad import VADIterator, load_silero_vad
from moonshine_onnx import MoonshineOnnxModel, load_tokenizer
from loguru import logger

SAMPLING_RATE = 16000
CHUNK_SIZE = 512
LOOKBACK_CHUNKS = 5
PAUSE_DURATION = 0.5  # Pause duration in seconds
MAX_SPEECH_SECS = 5

class WernickesArea:
    def __init__(self, model_name):
        self.model = MoonshineOnnxModel(model_name=model_name)
        self.tokenizer = load_tokenizer()
        self.vad_model = load_silero_vad(onnx=True)  # Load the VAD model
        self.vad_iterator = VADIterator(
            model=self.vad_model,
            sampling_rate=SAMPLING_RATE,
            threshold=0.5,
            min_silence_duration_ms=700,
        )

        self.queue = Queue()
        self.transcription_queue = Queue()
        self.listening_thread = threading.Thread(target=self._listen)
        self.listening_thread.daemon = True
        self.stop_event = threading.Event()
        self.transcribe_lock = threading.Lock()
        self.pause = False

        self.input_stream = InputStream(
            samplerate=SAMPLING_RATE, 
            blocksize=CHUNK_SIZE, 
            channels=1, 
            dtype=np.float32,
            callback=self._input_callback
        )


    def start_listening(self):
        self.start_time = time.time()
        self._transcribe(np.zeros(int(SAMPLING_RATE), dtype=np.float32))
        self.input_stream.start()
        self.listening_thread.start()
        

    def stop_listening(self):
        self.stop_event.set()
        self.input_stream.stop()
        self.listening_thread.join()
    
    def _soft_reset(self):
        self.vad_iterator.triggered = False
        self.vad_iterator.temp_end = 0
        self.vad_iterator.current_sample = 0

    def _input_callback(self, indata, frames, time, status):
        if status:
            logger.info("{file} Status: {status}", file=__file__, status=status)
        if not self.pause:
            self.queue.put((indata.copy().flatten(), status))

    def _transcribe(self, speech):
        with self.transcribe_lock:
            start = time.time()
            tokens = self.model.generate(speech[np.newaxis, :].astype(np.float32))
            logger.info("{file} Transcription ended in {duration} seconds", file=__file__, duration=round(time.time() - start,2))
            return self.tokenizer.decode_batch(tokens)[0]

    def _listen(self):
        speech_buffer = np.zeros(0, dtype=np.float32)
        recording = False
        lookback_size = LOOKBACK_CHUNKS * CHUNK_SIZE
        logger.info("{file} Listening", file=__file__)

        while not self.stop_event.is_set():
            try:
                chunk, status = self.queue.get(timeout=1)
            except Empty:
                continue
            
            speech_buffer = np.concatenate((speech_buffer, chunk))

            if not recording:
                speech_buffer = speech_buffer[-lookback_size:]

            speech_dict = self.vad_iterator(chunk)
            if speech_dict:
                if "start" in speech_dict and not recording:
                    recording = True
                    self.start_time = time.time()

                if "end" in speech_dict and recording:
                    recording = False
                    transcription = self._transcribe(speech_buffer)
                    if "Fred" in transcription:
                        self.transcription_queue.put(transcription)
                    else:
                        logger.info("{file} Throwing away: {transcription}", file=__file__, transcription=transcription)
                    speech_buffer = np.zeros(0, dtype=np.float32)

            elif recording:
                if (len(speech_buffer) / SAMPLING_RATE) > MAX_SPEECH_SECS:
                    logger.info("{file} Speech timeout", file=__file__)
                    recording = False
                    transcription = self._transcribe(speech_buffer)
                    if "Fred" in transcription:
                        self.transcription_queue.put(transcription)
                    else:
                        logger.info("{file} Throwing away: {transcription}", file=__file__, transcription=transcription)
                    speech_buffer = np.zeros(0, dtype=np.float32)
                    self._soft_reset()
                
                if time.time() - self.start_time > PAUSE_DURATION:
                    self.start_time = time.time()

        logger.info("{file} Done Listening", file=__file__)

    def get_transcription(self):
        try:
            return self.transcription_queue.get_nowait()
        except Empty:
            return None

# Example usage:
# listener = WernickesArea(model_name='path/to/moonshine/model')
# listener.start_listening()
# while True:
#     transcription = listener.get_transcription()
#     if transcription:
#         print("Transcription:", transcription)
