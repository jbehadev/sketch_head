import threading
import time

from freds_body import VirtualBrocasArea, Larynx, VirtualLarynx

thalamus_url = 'http://localhost:8000'

talker = Larynx()
talker.start()

talker.add_response('The moon has craters because its surface has been bombarded by meteoroids, asteroids, and comets over billions of years. Unlike Earth, the moon lacks a thick atmosphere to burn up incoming space debris, so these objects impact its surface directly, creating craters. The absence of weather, water, and tectonic activity on the moon means that these craters are preserved almost perfectly over time, providing a record of its ancient history.')
while True:
    pass

