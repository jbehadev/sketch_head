import openai
class ResponseGenerator:
    def __init__(self):
        self.transcription_queue = Queue()
        self.response_queue = Queue()
        self.response_thread = threading.Thread(target=self._generate_response)
        self.response_thread.daemon = True
        self.stop_event = threading.Event()

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
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=transcription,
                    max_tokens=50
                )
                response_text = response.choices[0].text.strip()
                self.response_queue.put(response_text)
            except Exception as e:
                print(f"Error generating response: {e}")

    def add_transcription(self, transcription):
        self.transcription_queue.put(transcription)

    def get_response(self):
        try:
            return self.response_queue.get_nowait()
        except Queue.Empty:
            return None