import serial
import time
import sys
import argparse
import random
from nicegui import app,ui


arg_parse = argparse.ArgumentParser(add_help=False)
arg_parse.add_argument('--env', required=True)

arguments, unknown = arg_parse.parse_known_args()

saved_event_name = ""

@ui.page('/')
def index():
    class arduino_mock:
        def readline(self):
            return b""
        
        def write(self, output):
            print(output)

    if(arguments.env == 'prod'):
        arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
    else:
        arduino = arduino_mock()

    def write_read(x):
        if type(x) == int:
            arduino.write(x.to_bytes(1, sys.byteorder))
        else:
            arduino.write(bytes(x, 'utf-8'))

    def write_list(event_list):
        [write_read(ev) for ev in event_list]

    def create_event():
        event = []
        # left eye color
        left_eye_color = tuple(int(left_color_picker.value.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        event.append('L')
        event.append(left_brightness_slider.value)
        event.append(left_eye_color[0])
        event.append(left_eye_color[1])
        event.append(left_eye_color[2])
        event.append('|')
        right_eye_color = tuple(int(right_color_picker.value.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        event.append('R')
        event.append(right_brightness_slider.value)
        event.append(right_eye_color[0])
        event.append(right_eye_color[1])
        event.append(right_eye_color[2])
        event.append('|')
        event.append('T')
        event.append(ascii(tilt_slider.value))
        event.append('|')
        event.append('S')
        event.append(ascii(swivel_slider.value))
        event.append('|')
        event.append('D')
        event.append(ascii(duration_slider.value))
        event.append('|')
        event.append('E')
        return event
    
    def create_random_event():
        event = []
        # left eye color
        event.append('L')
        event.append(random.randrange(1,250))
        event.append(random.randrange(1,250))
        event.append(random.randrange(1,250))
        event.append(random.randrange(1,250))
        event.append('|')
        event.append('R')
        event.append(random.randrange(1,250))
        event.append(random.randrange(1,250))
        event.append(random.randrange(1,250))
        event.append(random.randrange(1,250))
        event.append('|')
        event.append('T')
        event.append(ascii(random.randrange(1,250)))
        event.append('|')
        event.append('S')
        event.append(ascii(random.randrange(1,250)))
        event.append('|')
        event.append('D')
        event.append(ascii(random.randrange(50,200)))
        event.append('|')
        event.append('E')
        return event

    def play_event(event):
        ui.notify(event)
        if type(event) == list:
            write_list(event)
        else:
            write_list([*event])
        
        while True:
            line = arduino.readline()
            if line == b'':
                break
            else:
                log.push(line.decode().strip('\r\n'))

    def save_event_name(t):
        global saved_event_name
        saved_event_name = t.value

    def save_event(dialog):
        nonlocal saved_events
        saved_events.append({'name': saved_event_name, 'event': create_event()})
        event_table.update()
        dialog.close()
        app.storage.user['saved_events'] = saved_events

    def clear_events():
        nonlocal saved_events
        app.storage.user['saved_events'] = None
        saved_events.clear()
        event_table.update()

    columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
    ]

    if app.storage.user.get('saved_events', None) is not None:
        saved_events = app.storage.user['saved_events']
    else:
        saved_events = [
            {'name': 'Yes', 'event': "T20|D40|ET80|D40|E"},
            {'name': 'No', 'event': "S20|D40|ES80|D40|E"},
        ]

    with ui.column():

        ui.label('Control Fred')

        with ui.card():
            timer = ui.timer(4, lambda: play_event(create_random_event()))
            ui.switch('Random event generator', value=False).bind_value_to(timer, 'active')
            ui.label('Random Event Delay')
            delay_slider = ui.slider(min=2, max=60, value=4).props('label-always').bind_value_to(timer, 'interval')

        with ui.card():
            ui.label('Tilt')
            with ui.row().classes('w-full'):
                with ui.grid(columns=3).classes('w-full'):
                    ui.label(text="Down").classes('text-right')
                    tilt_slider = ui.slider(min=1, max=220, value=100).props('label-always').classes('w-full')
                    ui.label(text="Up")

            ui.label('Swivel')
            with ui.row().classes('w-full'):
                with ui.grid(columns=3).classes('w-full'):
                    ui.label(text="Left").classes('text-right')
                    swivel_slider = ui.slider(min=1, max=180, value=90).props('label-always').classes('w-full')
                    ui.label(text="Right")


            with ui.row().classes('w-full'):
                with ui.grid(columns=2).classes('w-full'):
                    with ui.column():
                        ui.label('Left Eye')
                        left_color_picker = ui.color_input(label='Right Color', value='#ff0000').picker.q_color.props('no-header no-footer default-view=palette')
                        ui.label('Brightness')
                        left_brightness_slider = ui.slider(min=0, max=255, value=150).props('label-always')
                    with ui.column():
                        ui.label('Right Eye')
                        right_color_picker = ui.color_input(label='Right Color', value='#ff0000').picker.q_color.props('no-header no-footer default-view=palette')
                        ui.label('Brightness')
                        right_brightness_slider = ui.slider(min=0, max=255, value=150).props('label-always')

            ui.label('Movement speed')
            duration_slider = ui.radio({400: 'Slow', 150: 'Medium', 50: 'Fast'},value=150).props('inline')

            ui.button('Instruct!', on_click=lambda: play_event(create_event())).classes('w-full')

        with ui.dialog() as dialog, ui.card():
            ui.input(label='Event Name', on_change=save_event_name)
            ui.button('Save', on_click=lambda: save_event(dialog))

        ui.button('Save Event', on_click=dialog.open).classes('w-full')



        ui.label('Saved Events - Click to play')
        event_table = ui.aggrid({'columnDefs': columns, 'rowData':saved_events})

        event_table.on('cellClicked', lambda s: play_event(s['args']['data']['event']))

        ui.button('Clear Saved Events', on_click=clear_events )

        ui.label('Event Log')
        log = ui.log(max_lines=1000).classes('w-full h-20')

        log.push(arduino.readline().decode())


    
ui.run(storage_secret="fred")

        

