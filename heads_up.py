import serial
import time

arduino = serial.Serial(port='/dev/tty.usbmodem141101', baudrate=9600, timeout=1)
def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
   
print(arduino.readline())
"""
while True:
    command = input("What?:")
    chunked = command.split(' ')
    print(chunked)
    write_read(chunked[0])
    write_read(ascii(int(chunked[1])))
    write_read('|')
    write_read('D')
    write_read(ascii(int(chunked[2])))
    write_read('|')
    write_read('E')
    time.sleep(1)
    while True:
        line = arduino.readline()
        if line == b'':
            break
        else:
            print(line)
"""
from nicegui import ui

def createEvent():
    write_read('T')
    write_read(ascii(tilt_slider.value))
    write_read('|')
    write_read('S')
    write_read(ascii(swivel_slider.value))
    write_read('|')
    write_read('D')
    write_read(ascii(duraction_slider.value))
    write_read('|')
    write_read('E')

ui.label('Control Fred')
tilt_slider = ui.slider(min=1, max=220, value=100)
swivel_slider = ui.slider(min=1, max=180, value=90)
duraction_slider = ui.slider(min=50, max=300, value=150)

ui.label().bind_text_from(tilt_slider, 'value')

ui.button('BUTTON', on_click=createEvent)

ui.run()

    

