import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json
from typing import List

class AppRunner(tk.Tk):
    """
    A class to represent AppRunner GUI application.

    Attributes:
    -----------
    apps : list
        A list of filepaths for executable applications.

    Methods:
    --------
    add_app(self) -> None:
        Adds a new application to the apps list.
    refresh_app_list(self) -> None:
        Refreshes the list of applications on the GUI.
    run_apps(self) -> None:
        Runs all applications listed in the apps list.
    load_apps(self) -> List[str]:
        Loads the list of applications from the 'apps.json' file.
    save_project(self) -> None:
        Saves the current project in a 'JSON' file.
    new_project(self) -> None:
        Resets the apps list.
    open_project(self) -> None:
        Opens an existing project from a 'JSON' file.
    undo_action(self) -> None:
        Undoes the previous action.
    cut_text(self) -> None:
        Cuts selected text.
    copy_text(self) -> None:
        Copies selected text.
    paste_text(self) -> None:
        Pastes the clipboard contents.
    show_about(self) -> None:
        Shows the 'About' info.
    """

    def __init__(self) -> None:
        """
        Initializes the AppRunner GUI application.

        Returns:
        --------
        None
        """
        super().__init__()
        self.apps: List[str] = self.load_apps()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the GUI elements.

        Returns:
        --------
        None
        """
        self.title('App Runner')
        self.geometry('700x350')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.create_widgets()
        self.create_menu_bar()

    def create_widgets(self) -> None:
        """
        Creates the GUI widgets.

        Returns:
        --------
        None
        """
        self.canvas = tk.Canvas(self, height=700, width=350, bg="#263D42")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.frame = tk.Frame(self, bg="white")
        self.frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.open_file_button = ttk.Button(self, text="Open File", command=self.add_app)
        self.open_file_button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.run_apps_button = ttk.Button(self, text="Run Apps", command=self.run_apps)
        self.run_apps_button.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=4, column=0, sticky="ew")

    def create_menu_bar(self) -> None:
        """
        Creates the GUI menu bar.

        Returns:
        --------
        None
        """
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_project)
        file_menu.add_command(label="Open", command=self.open_project)
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def add_app(self) -> None:
        """
        Adds a new application to the apps list.

        Returns:
        --------
        None
        """
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=(("executables", "*.exe"), ("all files", "*.*")))
        if filename:
            self.apps.append(filename)
            self.refresh_app_list()

    def refresh_app_list(self) -> None:
        """
        Refreshes the list of applications on the GUI.

        Returns:
        --------
        None
        """
        for widget in self.frame.winfo_children():
            widget.destroy()
        for app in self.apps:
            label = ttk.Label(self.frame, text=app, background="gray")
            label.pack()

    def run_apps(self) -> None:
        """
        Runs all applications listed in the apps list.

        Returns:
        --------
        None
        """
        for app in self.apps:
            subprocess.Popen(app, shell=True)

    def load_apps(self) -> List[str]:
        """
        Loads the list of applications from the 'apps.json' file.

        Returns:
        --------
        apps : list
            A list of filepaths for executable applications.
        """
        try:
            with open('apps.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_project(self) -> None:
        """
        Saves the current project in a 'JSON' file.

        Returns:
        --------
        None
        """
        filename = filedialog.asksaveasfilename(title="Save Project",
                                                filetypes=(("JSON files", "*.json"), ("all files", "*.*")),
                                                defaultextension=".json")
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.apps, f, indent=4)

    def new_project(self) -> None:
        """
        Resets the apps list.

        Returns:
        --------
        None
        """
        self.apps = []
        self.refresh_app_list()

    def open_project(self) -> None:
        """
        Opens an existing project from a 'JSON' file.

        Returns:
        --------
        None
        """
        filename = filedialog.askopenfilename(title="Open Project",
                                              filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
        if filename:
            with open(filename, 'r') as f:
                self.apps = json.load(f)
            self.refresh_app_list()

    def undo_action(self) -> None:
        """
        Undoes the previous action.

        Returns:
        --------
        None
        """
        # Placeholder for undo action functionality
        pass

    def cut_text(self) -> None:
        """
        Cuts selected text.

        Returns:
        --------
        None
        """
        # Placeholder for cut text functionality
        pass

    def copy_text(self) -> None:
        """
        Copies selected text.

        Returns:
        --------
        None
        """
        # Placeholder for copy text functionality
        pass

    def paste_text(self) -> None:
        """
        Pastes the clipboard contents.

        Returns:
        --------
        None
        """
        # Placeholder for paste text functionality
        pass

    def show_about(self) -> None:
        """
        Shows the 'About' info.

        Returns:
        --------
        None
        """
        messagebox.showinfo("About", "AppRunner Version 1.0\nCreated by Your Name")

if __name__ == '__main__':
    app = AppRunner()
    app.mainloop()