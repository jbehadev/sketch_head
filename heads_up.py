import serial
import time
import sys
from nicegui import ui


arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
def write_read(x):
    if type(x) == int:
        arduino.write(x.to_bytes(1, sys.byteorder))
    else:
        arduino.write(bytes(x, 'utf-8'))
   


def createEvent():
    # left eye color
    left_eye_color = tuple(int(left_color_picker.value.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    write_read('L')
    write_read(left_brightness_slider.value)
    write_read(left_eye_color[0])
    write_read(left_eye_color[1])
    write_read(left_eye_color[2])
    write_read('|')
    right_eye_color = tuple(int(right_color_picker.value.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    write_read('R')
    write_read(right_brightness_slider.value)
    write_read(right_eye_color[0])
    write_read(right_eye_color[1])
    write_read(right_eye_color[2])
    write_read('|')
    write_read('T')
    write_read(ascii(tilt_slider.value))
    write_read('|')
    write_read('S')
    write_read(ascii(swivel_slider.value))
    write_read('|')
    write_read('D')
    write_read(ascii(duration_slider.value))
    write_read('|')
    write_read('E')
    while True:
        line = arduino.readline()
        if line == b'':
            break
        else:
            log.push(line.decode().strip('\r\n'))
    

ui.label('Control Fred')

ui.label('Tilt')
with ui.grid(columns=2).classes('w-full'):
    tilt_slider = ui.slider(min=1, max=220, value=100)
    ui.label().bind_text_from(tilt_slider, 'value')

ui.label('Swivel')
with ui.grid(columns=2).classes('w-full'):
    swivel_slider = ui.slider(min=1, max=180, value=90)
    ui.label().bind_text_from(swivel_slider, 'value')

with ui.grid(columns=2).classes('w-full'):
    ui.label('Left Eye')
    ui.label('Right Eye')
with ui.grid(columns=6).classes('w-full'):
    left_color_picker = ui.color_input(label='Color', value='#ff0000')

    left_brightness_slider = ui.slider(min=0, max=255, value=150)
    ui.label().bind_text_from(left_brightness_slider, 'value')

    right_color_picker = ui.color_input(label='Color', value='#ff0000')

    right_brightness_slider = ui.slider(min=0, max=255, value=150)
    ui.label().bind_text_from(right_brightness_slider, 'value')

with ui.grid(columns=2).classes('w-full'):
    duration_slider = ui.radio({400: 'Slow', 150: 'Medium', 50: 'Fast'},value=150).props('inline')
    ui.label().bind_text_from(duration_slider, 'value')

ui.button('Instruct!', on_click=createEvent)

log = ui.log(max_lines=1000).classes('w-full h-20')

log.push(arduino.readline().decode())
ui.run()

    

