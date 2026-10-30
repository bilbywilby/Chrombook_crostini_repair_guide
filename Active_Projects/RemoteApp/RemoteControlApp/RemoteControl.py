from typing import Any, Dict

import kivy
kivy.require('2.0.0')
from kivy.adapters.ListAdapter import ListAdapter
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.RecycleView import RecycleView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput


Window.size = (360, 640)
PROFILES_STORE = JsonStore('profiles.json')


class RemoteControl(App):
    adapter: ObjectProperty(None)

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
        content_area.ViewClass = 'Button'
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
        available_profiles = PROFILES_STORE.keys()
        if not available_profiles:
            available_profiles = ["No Profiles Found"]
        profiles_spinner = Spinner(
            text="Select Profile",
            values=list(available_profiles),
            size_hint_x=None,
            width=100,
            font_size=14,
            background_color=[0,0,0,0],
            color=[1,1,1,1]
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

        device_type = Spinner(
            text="Select Device Type",
            values=["Smartphone", "Smart TV", "Streaming Device"],
            background_color=[0,0,0,0],
            color=[1,1,1,1]
        )

        popup_layout.add_widget(device_type)

        connect_button = Button(
            text="Connect",
            font_size=14,
        )
        connect_button.bind(
            on_press=lambda x: self.connect_device(popup, device_type.text, ip_input.text),
        )
        popup_layout.add_widget(connect_button)
        popup = Popup(
            title="Connect New Device",
            content=popup_layout,
            size_hint=(None, None),
            size=(400, 250),
            auto_dismiss=False,
        )
        popup.open()

    def connect_device(self, popup: Popup, device_type: str, ip: str) -> None:
        if ip:
            # Logic to connect to the device
            print(f"Connecting to {device_type} with IP: {ip}")
            popup.dismiss()
        else:
            error_popup = Popup(
                title="Invalid IP Address",
                content=Label(
                    text="Please enter a valid IP address.",
                    font_size=14,
                ),
                size_hint=(None, None),
                size=(250, 200),
            )
            error_popup.open()

    def load_profile(self, text: str) -> None:
        preferences = PROFILES_STORE.get(text, {}).get("preferences", {})
        if preferences:
            devices = preferences.get("devices", [])
            if self.adapter is None:
                self.adapter = ListAdapter(
                    data=devices,
                    selection_mode="single",
                    allow_empty_selection=True,
                    cls=Button,
                    use_default_colors=True,
                    sorted_keys=[],
                )
                self.adapter.bind(on_selection_change=self.on_device_selected)
                self.content_area.adapter = self.adapter
            else:
                self.adapter.data = devices
            success_popup = Popup(
                title="Profile Loaded",
                content=Label(
                    text=f"Profile '{text}' has been loaded.",
                    font_size=14,
                ),
                size_hint=(None, None),
                size=(250, 200),
            )
            success_popup.open()
        else:
            error_popup = Popup(
                title="Error Loading Profile",
                content=Label(
                    text=f"Profile '{text}' could not be loaded.",
                    font_size=14,
                ),
                size_hint=(None, None),
                size=(250, 200),
            )
            error_popup.open()

    def on_device_selected(self, adapter: Any, *args: Any) -> None:
        selected = self.adapter.selection
        if selected:
            device_name = self.adapter.data[selected[0]]
            # Logic to handle the selected device
            print(f"Selected Device: {device_name}")


if __name__ == "__main__":
    RemoteControl().run()