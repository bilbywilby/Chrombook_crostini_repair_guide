import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import json
import os
from typing import List, Dict


class AppRunner(tk.Tk):
    """
    This class initializes the App Runner GUI and all of its functionality.
    """

    APP_FILE_TYPES: tuple = (("executables", "*.exe"), ("all files", "*.*"))

    PROJECT_STRUCTURE: Dict[str, List[str]] = {
        'root': ['README.md', 'requirements.txt', '.gitignore'],
        'src': ['app.py', '__init__.py'],
        'docs': ['documentation.md'],
        'tests': ['test_app.py', '__init__.py']
    }

    FILE_PLACEHOLDERS: Dict[str, str] = {
        '.md': '# Project Title\n\nThis is a placeholder for documentation.',
        '.py': '#!/usr/bin/env python3\n\n"""Module docstring."""\n\ndef main() -> None:\n    pass\n\nif __name__ == "__main__":\n    main()',
        '.txt': '# Requirements or other text information',
        '.gitignore': '# Compiled python modules.\n*.pyc\n\n# Setuptools distribution folder.\ndist/'
    }

    def __init__(self) -> None:
        """
        Initializes the AppRunner class and defines the GUI window properties such as title and geometry.
        """

        super().__init__()
        self.title('App Runner')
        self.geometry('700x350')
        self.apps: List[str] = self.load_apps()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Configures the UI elements.
        """

        self.create_widgets()
        self.create_menu_bar()

    def create_widgets(self) -> None:
        """
        Creates the UI elements and places them at their required positions.
        """

        self.canvas = tk.Canvas(self, height=700, width=350, bg="#263D42")
        self.canvas.pack(side='left', fill='both', expand=True)

        self.frame = tk.Frame(self, bg="white")
        self.frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

        self.open_file_button = tk.Button(self, text="Open File", padx=10, pady=5, command=self.add_app)
        self.open_file_button.pack()

        self.run_apps_button = tk.Button(self, text="Run Apps", padx=10, pady=5, command=self.run_apps)
        self.run_apps_button.pack()

        self.create_project_button = tk.Button(self, text="Create Project", padx=10, pady=5, command=self.create_project)
        self.create_project_button.pack()

        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill='both', expand=True)
        self.refresh_app_list()

    def create_menu_bar(self) -> None:
        """
        Creates the UI menu bar.
        """

        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.add_app)
        file_menu.add_command(label="Save", command=self.save_apps)
        file_menu.add_command(label="Create Project", command=self.create_project)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def add_app(self) -> None:
        """
        Overwrites the selected executable file, with the originally selected executable. Adds executable with
        optional command line arguments to be run later.
        """

        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=self.APP_FILE_TYPES)

        if filename:
            args = simpledialog.askstring("Arguments", "Enter arguments (optional):")

            app_with_args = f"{filename} {args}" if args else filename
            self.apps.append(app_with_args)
            self.refresh_app_list()

    def refresh_app_list(self) -> None:
        """
        Refreshes the listbox to load all elements
        """

        self.listbox.delete(0, tk.END)

        for app in self.apps:
            self.listbox.insert(tk.END, app)

    def run_apps(self) -> None:
        """
        Runs all of the apps in the class list of apps.
        """

        for app in self.apps:
            subprocess.Popen(app, shell=True)

    def load_apps(self) -> List[str]:
        """
        Loads the saved list of executables with optional command line arguments.
        """

        try:
            with open('apps.json', 'r') as f:
                return json.load(f)

        except FileNotFoundError:
            return []

    def save_apps(self) -> None:
        """
        Saves the current list of executables with optional command line arguments.
        """

        with open('apps.json', 'w') as f:
            json.dump(self.apps, f, indent=4)

    def create_project(self) -> None:
        """
        Creates a new project with folder hierarchy and initial blank files with appropriate extensions
        """

        project_name = filedialog.askstring("Project Name", "Enter the name of the new project:")

        if project_name:
            base_path = filedialog.askdirectory()
            self.create_project_structure(base_path, project_name)
            messagebox.showinfo("Success", f"Project '{project_name}' has been created.")

    def create_project_structure(self, base_path: str, project_name: str) -> None:
        """
        Generates the folder and file structure for a new project - in which the root, src, docs and test folders
        are present.
        """

        for folder, files in self.PROJECT_STRUCTURE.items():
            folder_path = os.path.join(base_path, project_name, folder if folder != 'root' else '')
            os.makedirs(folder_path, exist_ok=True)

            for file in files:
                file_path = os.path.join(folder_path, file)
                file_extension = os.path.splitext(file)[1]

                with open(file_path, 'w') as f:
                    f.write(self.FILE_PLACEHOLDERS.get(file_extension, ''))


if __name__ == '__main__':
    app = AppRunner()
    app.mainloop()