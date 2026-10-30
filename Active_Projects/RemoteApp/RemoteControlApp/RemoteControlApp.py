from typing import Any, Dict, Optional

import kivy
from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

kivy.require('2.0.0')

# Set the default window size
Window.size = (360, 640)

# Initialize the store for user profiles
PROFILES_STORE = JsonStore('profiles.json')


class RemoteControl(App):
    adapter: ObjectProperty(None)

    def build(self) -> BoxLayout:
        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=5,
            spacing=5
        )

        self.bottom_nav = self.create_bottom_nav()
        self.content_area = self.create_content_area()
        self.settings = self.create_settings()
        self.active_screen = self.content_area
        self.top_bar = self.create_top_bar()

        self.main_layout.add_widget(self.bottom_nav)
        self.main_layout.add_widget(self.active_screen)
        self.main_layout.add_widget(self.top_bar)

        return self.main_layout

    def create_bottom_nav(self) -> BoxLayout:
        bottom_nav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=5
        )
        media_btn = Button(
            text='Media',
            font_size=14,
            on_press=self.show_media
        )
        volume_btn = Button(
            text='Volume',
            font_size=14,
            on_press=self.show_volume
        )
        settings_btn = Button(
            text='Settings',
            font_size=14,
            on_press=self.show_settings
        )

        bottom_nav.add_widget(media_btn)
        bottom_nav.add_widget(volume_btn)
        bottom_nav.add_widget(settings_btn)

        return bottom_nav

    def create_content_area(self) -> RecycleView:
        rv = RecycleView()
        rv.viewclass = 'Button'
        rv.data = [{'text': 'Play', 'on_press': self.execute_command},
                   {'text': 'Pause', 'on_press': self.execute_command},
                   {'text': 'Next', 'on_press': self.execute_command},
                   {'text': 'Previous', 'on_press': self.execute_command}]
        return rv

    def create_volume_controls(self) -> BoxLayout:
        volume_controls = BoxLayout(
            orientation='vertical',
            spacing=5
        )
        volume_up = Button(
            text='Volume Up',
            font_size=14,
            on_press=self.execute_command
        )
        volume_down = Button(
            text='Volume Down',
            font_size=14,
            on_press=self.execute_command
        )

        volume_controls.add_widget(volume_up)
        volume_controls.add_widget(volume_down)

        return volume_controls

    def create_settings(self) -> BoxLayout:
        settings = BoxLayout(
            orientation='vertical',
            spacing=5
        )
        settings_label = Label(
            text='Settings',
            halign='center',
            font_size=22,
            text_size=self.main_layout.size
        )
        backup_button = Button(
            text='Backup Data',
            font_size=14,
            on_press=self.backup_data
        )
        log_out_button = Button(
            text='Log Out',
            font_size=14,
            on_press=self.log_out
        )

        settings.add_widget(settings_label)
        settings.add_widget(backup_button)
        settings.add_widget(log_out_button)

        return settings

    def create_spinner(self) -> Spinner:
        available_profiles = PROFILES_STORE.keys()
        available_profiles = ['No Profiles Found'] if not available_profiles else available_profiles
        profiles_spinner = Spinner(
            text='Select Profile',
            values=list(available_profiles),
            size_hint_x=None,
            width=100,
            font_size=14,
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1]
        )
        profiles_spinner.bind(text=self.load_profile)
        return profiles_spinner

    def create_top_bar(self) -> BoxLayout:
        top_bar = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5,
            padding=5
        )
        profiles_spinner = self.create_spinner()
        top_bar.add_widget(profiles_spinner)
        top_bar.add_widget(Label(
            text='Remote Control',
            halign='center',
            font_size=22,
            text_size=self.main_layout.size
        ))
        top_bar.add_widget(Button(
            text='Connect',
            size_hint_x=None,
            width=100,
            font_size=14,
            on_press=self.show_device_popup
        ))
        return top_bar

    def show_media(self, instance: Button) -> None:
        self.change_active_screen(self.content_area)
        self.bottom_nav.children[0].background_color = [0, 1, 0, 1]
        self.bottom_nav.children[1].background_color = [1, 1, 1, 1]
        self.bottom_nav.children[2].background_color = [1, 1, 1, 1]

    def show_volume(self, instance: Button) -> None:
        volume_controls = self.create_volume_controls()
        self.change_active_screen(volume_controls)
        self.bottom_nav.children[0].background_color = [1, 1, 1, 1]
        self.bottom_nav.children[1].background_color = [0, 1, 0, 1]
        self.bottom_nav.children[2].background_color = [1, 1, 1, 1]

    def show_settings(self, instance: Button) -> None:
        self.change_active_screen(self.settings)
        self.bottom_nav.children[0].background_color = [1, 1, 1, 1]
        self.bottom_nav.children[1].background_color = [1, 1, 1, 1]
        self.bottom_nav.children[2].background_color = [0, 1, 0, 1]

    def show_device_popup(self, instance: Button) -> None:
        popup_layout = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=5
        )
        popup_layout.add_widget(Label(
            text='Enter Device IP:',
            font_size=18
        ))
        ip_input = TextInput(
            text='',
            multiline=False,
            font_size=14
        )
        popup_layout.add_widget(ip_input)

        device_type = Spinner(
            text='Select Device Type',
            values=['Smartphone', 'Smart TV', 'Streaming Device'],
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1]
        )
        popup_layout.add_widget(device_type)

        connect_button = Button(
            text='Connect',
            size_hint_y=None,
            height=50,
            on_press=self.connect_to_device
        )
        popup_layout.add_widget(connect_button)

        self.device_popup = Popup(
            title='Device Connection',
            content=popup_layout,
            size_hint=(None, None),
            size=(400, 400),
            auto_dismiss=False
        )
        self.device_popup.open()

    def change_active_screen(self, new_screen) -> None:
        self.main_layout.remove_widget(self.active_screen)
        self.active_screen = new_screen
        self.main_layout.add_widget(self.active_screen)

    def connect_to_device(self, instance: Button) -> None:
        ip_input = self.device_popup.content.children[1]
        device_type = self.device_popup.content.children[2]
        if ip_input.text == '':
            self.display_error('IP address cannot be empty!')
            return

        device_info = {'ip': ip_input.text, 'type': device_type.text}
        self.display_message(f'Connecting to {device_type.text} with IP: {ip_input.text}...')
        # Logic to connect to the device

    def load_profile(self, spinner_text: str) -> None:
        if spinner_text != 'No Profiles Found':
            profile_data = PROFILES_STORE.get(spinner_text, {}).get('preferences', {})
            self.display_message(f'Profile "{spinner_text}" loaded successfully.')
            # Logic to update UI with profile data

    def save_profile(self, profile_name: str, profile_data: Dict[str, Any]) -> None:
        PROFILES_STORE.put(profile_name, **profile_data)
        self.display_message(f'Profile "{profile_name}" saved successfully.')

    def delete_profile(self, profile_name: str) -> None:
        if PROFILES_STORE.exists(profile_name):
            PROFILES_STORE.delete(profile_name)
            self.display_message(f'Profile "{profile_name}" deleted successfully.')
        else:
            self.display_error(f'Profile "{profile_name}" does not exist!')

    def backup_data(self, instance: Button) -> None:
        backup_data = {'profiles': PROFILES_STORE._data}
        # Logic to back up the data

    def log_out(self, instance: Button) -> None:
        self.stop()

    def display_message(self, message: str) -> None:
        message_popup = Popup(
            title='Message',
            content=Label(text=message, font_size=18),
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=False
        )
        message_popup.open()

    def display_error(self, error: Optional[str] = None) -> None:
        if error is not None:
            error_layout = BoxLayout(
                orientation='vertical',
                padding=10,
                spacing=5
            )
            error_layout.add_widget(Label(
                text='Error:',
                font_size=20
            ))
            error_layout.add_widget(Label(
                text=error,
                font_size=14,
                halign='center'
            ))

            error_popup = Popup(
                title='Error',
                content=error_layout,
                size_hint=(None, None),
                size=(400, 200),
                auto_dismiss=True
            )
        else:
            error_popup = Popup(
                title='Error',
                content=Label(text='An error occurred!', font_size=20),
                size_hint=(None, None),
                size=(300, 150),
                auto_dismiss=True
            )
        error_popup.open()

    def execute_command(self, instance: Button) -> None:
        command = instance.text
        self.display_message(f'Executing command: {command}')

if __name__ == '__main__':
    RemoteControl().run()
    