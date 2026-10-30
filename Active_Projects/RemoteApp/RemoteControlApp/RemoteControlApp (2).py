from typing import Any, Dict

from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

Window.size = (360, 640)
PROFILES_STORE = JsonStore('profiles.json')


class RemoteControl(App):
    device_buttons = ListProperty([])

    def build(self) -> BoxLayout:
        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=5,
            spacing=5,
        )
        self.top_bar = self.create_top_bar()
        self.content_area = self.create_content_area()
        self.bottom_bar = self.create_bottom_bar()
        self.main_layout.add_widget(self.top_bar)
        self.main_layout.add_widget(self.content_area)
        self.main_layout.add_widget(self.bottom_bar)
        return self.main_layout

    def create_top_bar(self) -> BoxLayout:
        top_bar = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5,
            padding=5,
        )
        profiles_spinner = self.create_spinner()
        top_bar.add_widget(profiles_spinner)
        top_bar.add_widget(
            Label(
                text="Remote Control",
                halign="center",
                font_size=22,
                text_size=self.main_layout.size,
            ),
        )
        top_bar.add_widget(
            Button(
                text="Connect",
                size_hint_x=None,
                width=100,
                font_size=14,
                on_press=self.show_device_popup,
            ),
        )
        return top_bar

    def create_content_area(self) -> RecycleView:
        content_area = RecycleView()
        self.devices_list = GridLayout(
            cols=1,
            size_hint_y=None,
            padding=10,
            spacing=10,
        )
        self.devices_list.bind(minimum_height=self.devices_list.setter("height"))
        content_area.add_widget(self.devices_list)
        return content_area

    def create_main_layout(self) -> BoxLayout:
        pass

    def create_bottom_bar(self) -> BoxLayout:
        bottom_bar = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5,
        )
        bottom_bar.add_widget(
            Button(
                text="Settings",
                font_size=14,
            ),
        )
        bottom_bar.add_widget(
            Button(
                text="Help",
                font_size=14,
            ),
        )
        return bottom_bar

    def create_spinner(self) -> Spinner:
        profiles_spinner = Spinner(
            text="Select Profile",
            values=list(PROFILES_STORE.keys()),
            size_hint_x=None,
            width=100,
            font_size=14,
        )
        profiles_spinner.bind(text=self.load_profile)
        return profiles_spinner

    def show_device_popup(self, instance: Button) -> None:
        popup_layout = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=5,
        )
        popup_layout.add_widget(
            Label(
                text="Enter Device IP:",
                font_size=18,
            ),
        )
        ip_input = TextInput(
            text="",
            multiline=False,
            font_size=14,
        )
        popup_layout.add_widget(ip_input)
        connect_button = Button(
            text="Connect",
            font_size=14,
        )
        connect_button.bind(
            on_press=lambda x: self.connect_device(ip_input.text),
        )
        popup_layout.add_widget(connect_button)
        popup = Popup(
            title="Connect New Device",
            content=popup_layout,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False,
        )
        popup.open()

    def connect_device(self, ip: str) -> None:
        # Logic to connect to the device
        pass

    def load_profile(self, text: str) -> None:
        self.devices_list.clear_widgets()
        self.device_buttons.clear()
        preferences = PROFILES_STORE.get(text, {}).get("preferences", {})
        devices = preferences.get("devices", [])
        adapter = ListAdapter(
            data=devices,
            selection_mode="single",
            allow_empty_selection=True,
            cls=Button,
            use_default_colors=True,
        )
        adapter.bind(on_selection_change=self.on_device_selected)
        self.devices_list.add_widget(adapter)

    def on_device_selected(self) -> None:
        selected = self.devices_list.adapter.selection
        if selected:
            device_name = self.devices_list.adapter.data[selected[0]]
            # Logic to handle the selected device
            print(f"Selected Device: {device_name}")


if __name__ == "__main__":
    RemoteControl().run()