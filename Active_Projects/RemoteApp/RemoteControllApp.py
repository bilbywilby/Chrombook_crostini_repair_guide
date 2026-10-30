import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ListProperty, ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

kivy.require('2.0.0')

class RemoteControlApp(App):
    profiles_store = JsonStore('profiles.json')
    current_profile = ObjectProperty(None)
    device_buttons = ListProperty([])

    def build(self):
        Window.size = (360, 640)
        self.setup_ui()
        self.load_profile(self.profile_spinner.text)
        return self.main_layout

    def setup_ui(self):
        self.profile_spinner = self.create_spinner()
        self.top_bar = self.create_top_bar()
        self.content_area = self.create_content_area()
        self.bottom_bar = self.create_bottom_bar()
        self.main_layout = self.create_main_layout()

    def create_spinner(self):
        """
        Creates a Spinner widget for profile selection and binds it to the corresponding function.
        """
        profile_spinner = Spinner(
            text='Select Profile',
            values=self.profiles_store.keys(),
            size_hint_x=None,
            width=100,
            font_size=14
        )
        profile_spinner.bind(text=self.load_profile)
        return profile_spinner

    def create_top_bar(self):
        """
        Creates a BoxLayout containing the profile Spinner, the Remote Control app label, and a Connect button.
        """
        top_bar = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5,
            padding=5
        )
        top_bar.add_widget(self.profile_spinner)
        top_label = Label(
            text='Remote Control App',
            halign='center',
            text_size=self.main_layout.size,
            font_size=22
        )
        top_bar.add_widget(top_label)
        connect_button = Button(
            text='Connect',
            size_hint_x=None,
            width=100,
            font_size=14,
            on_press=self.show_device_popup
        )
        top_bar.add_widget(connect_button)
        return top_bar

    def create_content_area(self):
        """
        Creates a ScrollView widget that contains a GridLayout of buttons for controlling devices.
        """
        content_area = ScrollView()
        grid_layout = GridLayout(
            cols=2,
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        content_area.add_widget(grid_layout)
        return content_area

    def create_main_layout(self):
        """
        Creates a BoxLayout containing the app's UI components.
        """
        main_layout = BoxLayout(
            orientation='vertical',
            padding=5,
            spacing=5
        )
        main_layout.add_widget(self.top_bar)
        main_layout.add_widget(self.content_area)
        main_layout.add_widget(self.bottom_bar)
        return main_layout

    def create_bottom_bar(self):
        """
        Creates a BoxLayout containing the Settings and Help buttons.
        """
        bottom_bar = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5
        )
        settings_button = Button(
            text='Settings',
            font_size=14
        )
        help_button = Button(
            text='Help',
            font_size=14
        )
        bottom_bar.add_widget(settings_button)
        bottom_bar.add_widget(help_button)
        return bottom_bar

    def show_device_popup(self, instance):
        """
        Displays a popup window for entering the IP address of a device to connect to.
        """
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
        connect_button = Button(
            text='Connect',
            font_size=14
        )
        connect_button.bind(on_press=lambda x: self.connect_device(ip_input.text))
        popup_layout.add_widget(connect_button)
        popup = Popup(
            title='Connect New Device',
            content=popup_layout,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False
        )
        popup.open()

    def connect_device(self, ip):
        """
        Placeholder function for connecting to a device.
        """
        # Replace with actual code to connect to a device
        pass

    def load_profile(self, text):
        """
        Loads the selected profile and updates the device buttons accordingly.
        """
        self.current_profile = self.profiles_store.get(text, {}).get('preferences', {})
        self.update_device_buttons()

    def update_device_buttons(self):
        """
        Updates the device buttons based on the current profile's device preferences.
        """
        content_area = self.content_area.children[0]
        grid_layout = content_area.children[0]
        grid_layout.clear_widgets()
        for device_name in self.current_profile.get('devices', []):
            btn = Button(
                text=device_name,
                size_hint_y=None,
                height=40,
                font_size=14
            )
            self.device_buttons.append(btn)
            grid_layout.add_widget(btn)

if __name__ == '__main__':
    RemoteControlApp().run()
