# main_script.py

import argparse
import random
from nicegui import ui, app
from pathlib import Path
import requests


# API endpoint
EVENT_MANAGER_URL = 'http://localhost:8000'  # Adjust if event_manager runs on a different host or port

saved_event_name = ""

@ui.page('/')
def index():
    def create_event():
        event = []
        # Left eye color
        left_eye_color = tuple(int(left_color_picker.value.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        event.append('L')
        event.append(left_brightness_slider.value)
        event.append(left_eye_color[0])
        event.append(left_eye_color[1])
        event.append(left_eye_color[2])
        event.append('|')
        # Right eye color
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
        event.append('L')
        event.append(random.randint(1, 250))
        event.extend([random.randint(1, 250) for _ in range(3)])
        event.append('|')
        event.append('R')
        event.append(random.randint(1, 250))
        event.extend([random.randint(1, 250) for _ in range(3)])
        event.append('|')
        event.append('T')
        event.append(random.randint(1, 250))
        event.append('|')
        event.append('S')
        event.append(random.randint(1, 250))
        event.append('|')
        event.append('D')
        event.append(random.randint(50, 200))
        event.append('|')
        event.append('E')
        return event

    def play_event(event):
        ui.notify(event)
        # Send event to event_manager API
        response = requests.post(f'{EVENT_MANAGER_URL}/play_event', json={'event': event})
        if response.status_code == 200:
            log.push(f"Event played: {event}")
        else:
            log.push(f"Failed to play event: {response.text}")

    def save_event_name(t):
        global saved_event_name
        saved_event_name = t.value

    def save_event(dialog):
        event = create_event()
        # Send event to event_manager API
        response = requests.post(f'{EVENT_MANAGER_URL}/save_event', json={'name': saved_event_name, 'event': event})
        if response.status_code == 200:
            saved_events.append({'name': saved_event_name, 'event': event})
            event_table.update()
            dialog.close()
        else:
            ui.notify(f"Failed to save event: {response.text}")

    def clear_events():
        response = requests.post(f'{EVENT_MANAGER_URL}/clear_events')
        if response.status_code == 200:
            saved_events.clear()
            event_table.update()
        else:
            ui.notify(f"Failed to clear events: {response.text}")

    def load_saved_events():
        response = requests.get(f'{EVENT_MANAGER_URL}/saved_events')
        if response.status_code == 200:
            return response.json().get('saved_events', [])
        else:
            ui.notify(f"Failed to load saved events: {response.text}")
            return []

    # UI Components
    columns = [{'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'}]
    saved_events = load_saved_events()

    app.add_static_files('/static', Path(__file__).resolve().parent / 'static')

    with ui.header(elevated=True).style('background-color: #3874c8'):
        ui.image('/static/fredhead.jpg').style('width:50px')
        ui.label('Fred Head Control Interface')

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
                    left_color_picker = ui.color_input(label='Left Color', value='#ff0000')
                    left_color_picker.picker.q_color.props('no-header no-footer default-view=palette')
                    ui.label('Brightness')
                    left_brightness_slider = ui.slider(min=0, max=255, value=150).props('label-always')
                with ui.column():
                    ui.label('Right Eye')
                    right_color_picker = ui.color_input(label='Right Color', value='#ff0000')
                    right_color_picker.picker.q_color.props('no-header no-footer default-view=palette')
                    ui.label('Brightness')
                    right_brightness_slider = ui.slider(min=0, max=255, value=150).props('label-always')

        ui.label('Movement speed')
        duration_slider = ui.radio({400: 'Slow', 150: 'Medium', 50: 'Fast'}, value=150).props('inline')

        ui.button('Instruct!', on_click=lambda: play_event(create_event())).classes('w-full')

    with ui.dialog() as dialog, ui.card():
        ui.input(label='Event Name', on_change=save_event_name)
        ui.button('Save', on_click=lambda: save_event(dialog))

    ui.button('Save Event', on_click=dialog.open).classes('w-full')

    ui.label('Saved Events - Click to play')
    event_table = ui.aggrid({'columnDefs': columns, 'rowData': saved_events})

    event_table.on('cellClicked', lambda s: play_event(s['args']['data']['event']))

    ui.button('Clear Saved Events', on_click=clear_events)

    ui.label('Event Log')
    log = ui.log(max_lines=1000).classes('w-full h-20')

ui.run(storage_secret="fred")
