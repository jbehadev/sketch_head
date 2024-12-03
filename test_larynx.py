import threading
import time

from freds_body import VirtualBrocasArea, Larynx

thalamus_url = 'http://localhost:8000'

talker = Larynx()
talker.start()

talker.add_response('Fred the head says something is happening')
while True:
    pass

