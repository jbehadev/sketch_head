import threading
import time

from freds_body import VirtualBrocasArea, Larynx, VirtualLarynx

thalamus_url = 'http://localhost:8000'

talker = VirtualLarynx()
talker.start()

talker.add_response('Fred the head says something is happening')
while True:
    pass

