import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import json
import os
from typing import List, Dict

class FileManager(tk.Tk):
    """
    Initializes the FileManager class with a GUI and all of its necessary functionality.
    """

    def __init__(self) -> None:
        """
         Initializes the FileManager class and defines the GUI window properties
         such as title and geometry. Also, loads the saved list of executables.
        """
        super().__init__()
        self.title('File Manager')
        self.geometry('800x400')
        self.apps: List[str] = self.load_apps()
        self.create_widgets()
        self.create_menu_bar()

    def create_widgets(self) -> None:
        """
        Creates the UI elements and places them at their required positions.
        """
        self.canvas = tk.Canvas(self, height=800, width=400, bg="#263D42")
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

    def create_menu_bar(self):
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

    def add_app(self):
        """
        Adds executable and optional command-line arguments to the list of apps.
        """
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=self.get_filetypes())

        if filename:
            args = self.get_arguments()
            app_with_args = f"{filename} {args}" if args else filename
            self.apps.append(app_with_args)
            self.refresh_app_list()

    def run_apps(self):
        """
        Runs all of the executables in the list of apps.
        """
        for app in self.apps:
            try:
                subprocess.Popen(app, shell=True, encoding='utf-8', errors='ignore')
            except OSError as error:
                messagebox.showerror("Error", f'Cannot run "{app}": {error}')

    def refresh_app_list(self):
        """
        Refreshes the listbox to load all elements.
        """
        self.listbox.delete(0, tk.END)
        for app in self.apps:
            self.listbox.insert(tk.END, app)

    def load_apps(self):
        """
        Loads the saved list of executables with optional command-line arguments.
        """
        try:
            with open('apps.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_apps(self):
        """
        Saves the current list of executables with optional command-line arguments.
        """
        with open('apps.json', 'w') as f:
            json.dump(self.apps, f, indent=4)

    def create_project(self):
        """
        Creates a new project with folder hierarchy and initial blank files with appropriate extensions.
        """
        project_name = self.get_project_name()
        if project_name:
            base_path = self.get_basepath()
            if base_path:
                self.create_project_structure(base_path, project_name)
                messagebox.showinfo("Success", f"Project '{project_name}' has been created.")

    @staticmethod
    def create_project_structure(base_path: str, project_name: str):
        """
        Creates the folder and file structure for a new project.
        """
        project_folder = os.path.join(base_path, project_name)
        os.makedirs(project_folder, exist_ok=True)

        for folder, files in FileManager.PROJECT_STRUCTURE.items():
            folder_path = os.path.join(project_folder, folder if folder != 'root' else '')
            os.makedirs(folder_path, exist_ok=True)

            for file in files:
                file_path = os.path.join(folder_path, file)
                file_extension = os.path.splitext(file)[1]

                with open(file_path, 'w') as f:
                    f.write(FileManager.FILE_PLACEHOLDERS.get(file_extension, ''))

    @staticmethod
    def get_arguments() -> str:
        """
        Gets the optional command-line arguments from the user.
        """
        args = filedialog.askstring("Arguments", "Enter arguments (optional):")
        return args.strip() if args else ""

    @staticmethod
    def get_filetypes() -> List[str]:
        """
        Gets the filetypes that can be selected by the user for the file dialog.
        """
        filetypes = [("executables", "*.exe"), ("all files", "*.*")]
        return filetypes

    @staticmethod
    def get_project_name() -> str:
        """
        Gets the project name from the user.
        """
        project_name = filedialog.askstring("Project Name", "Enter the name of the new project:")
        return project_name.strip() if project_name else ""

    @staticmethod
    def get_basepath() -> str:
        """
        Gets the folder path where the new project will be created.
        """
        base_path = filedialog.askdirectory()
        return base_path.strip() if base_path else ""

    PROJECT_STRUCTURE: Dict[str, List[str]] = {
        'root': ['README.md', 'requirements.txt', '.gitignore'],
        'src': ['main.py', '__init__.py'],
        'docs': ['documentation.md'],
        'tests': ['test_main.py', '__init__.py']
    }

    FILE_PLACEHOLDERS: Dict[str, str] = {
        '.md': '# Project Title\n\nThis is a placeholder for documentation.',
        '.py': '#!/usr/bin/env python3\n\n"""Module docstring."""\n\ndef main() -> None:\n    pass\n\nif __name__ == "__main__":\n    main()',
        '.txt': '# Requirements or other text information',
        '.gitignore': '# Compiled python modules.\n*.pyc\n\n# Setuptools distribution folder.\ndist/'
    }


if __name__ == '__main__':
    app = FileManager()
    app.mainloop()