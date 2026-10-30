import json
import logging
import pathlib
import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from enum import Enum
from typing import List, Optional, Tuple


class FileType(Enum):
    MARKDOWN = ".md"
    PYTHON = ".py"
    TEXT = ".txt"
    GITIGNORE = ".gitignore"

    def get_placeholder_file_path(self, app_manager: "AppManager") -> pathlib.Path:
        return app_manager.RESOURCE_DIR / f"placeholders/{self.name.lower()}_{app_manager.__class__.__name__}.txt"

    def get_placeholder_content(self, app_manager: "AppManager", filename: str) -> str:
        try:
            placeholder_file = self.get_placeholder_file_path(app_manager)
            with open(placeholder_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            app_manager.logging.warning(
                f"{filename}: Placeholder content for {self.name} not found"
            )
        except Exception as e:
            app_manager.logging.exception(
                f"{filename}: Failed to read placeholder content from {placeholder_file}"
            )
        return ""

    def is_text_file(self) -> bool:
        return self in (FileType.MARKDOWN, FileType.PYTHON, FileType.TEXT)


class AppManager(tk.Tk):
    """This class manages the applications and creates new project structures."""

    SUPPORTED_APP_FILETYPES = [("Executables", "*.exe"), ("All Files", "*.*")]

    CONFIG_FILE_NAME = "applications.json"
    CONFIG_FILE_PATH = pathlib.Path.home() / ".config" / CONFIG_FILE_NAME

    PROJECT_NAME_PROMPT = "Project Name"
    PROJECT_NAME_INPUT = "Enter the name of the new project:"
    CONFIRMATION_TITLE = "Confirmation"
    CONFIRMATION_TEXT = "Create a new project?"

    RESOURCE_DIR = pathlib.Path(__file__).parent / "resources"

    def __init__(self) -> None:
        super().__init__()
        self.title("App Manager")
        self.geometry("700x350")

        self.main_canvas = tk.Canvas(
            self, bg="#263D42", highlightthickness=0)
        self.list_frame = tk.Frame(
            self.main_canvas, bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            self.main_canvas, orient="vertical", command=self.list_frame.yview
        )
        self.list_frame.configure(yscroll=self.scrollbar.set)
        self.list_frame.pack(side="left", fill="y", expand=True)
        self.scrollbar.pack(side="right",fill="y", expand=False)
        self.main_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.main_canvas.bind("<Configure>", self._on_resize)
        self.main_canvas.pack(side="top", fill="both", expand=True)

        # Create listbox for displaying projects
        self.project_listbox = ProjectListBox(self.list_frame)
        self.project_listbox.grid(row=0, column=0, sticky="nswe")

        # Buttons to add/remove projects
        add_button = AddButton(self.list_frame, self.project_listbox)
        remove_button = RemoveButton(self.list_frame, self.project_listbox)
        buttons_frame = tk.LabelFrame(self.list_frame, text="Actions")
        buttons_frame.grid(row=1, column=0, padx=5, pady=(5, 0))
        add_button.pack(in_=buttons_frame),
        remove_button.pack(in_=buttons_frame)

        # Frame for showing application details
        app_details_frame = AppDetailsFrame(self.list_frame)
        app_details_frame.grid(row=1, column=1, padx=5, pady=5)

        # Bind events
        self.project_listbox.bind("<<Select>>", app_details_frame.show_app_info)

        # Load initial data (if any) and display it in the UI
        if "projects" in config:
            project_data = json.loads(config["projects"])
            for proj_name in sorted(project_data):
                self.project_listbox.add_item(proj_name)

    def _on_resize(self, event):
        """Adjust scrollbar when main canvas is resized."""
        self.list_frame.configure(width=event.width - 2*BORDERWIDTH)
        self.scrollbar.configure(command=self.list_frame.yview),
import os

class AppManager(tk.Tk):
    # ...

    def create_project_structure(self) -> None:
        """This method prompts the user for a project name and location, and creates a pre-determined directory structure for the project."""
        project_name = simpledialog.askstring(
            self.PROJECT_NAME_PROMPT, self.PROJECT_NAME_INPUT
        )
        if project_name and messagebox.askyesno(self.CONFIRMATION_TITLE, self.CONFIRMATION_TEXT):
            base_path = filedialog.askdirectory()
            if base_path:
                project_dir = pathlib.Path(base_path) / project_name
                os.makedirs(project_dir, exist_ok=True)
                for folder, files in self.get_project_structure().items():
                    folder_path = project_dir / folder if folder != "root" else project_dir
                    os.makedirs(folder_path, exist_ok=True)
                    for file in files:
                        file_extension = pathlib.Path(file).suffix.lower()
                        file_path = folder_path / file
                        content = FileType(file_extension).get_placeholder_content(
                            self, file_path.name
                        )
                        try:
                            file_path.write_text(content, encoding="utf-8")
                        except Exception as e:
                            self.logging.exception(f"Failed to create {file_path}: {e}")
                            messagebox.showwarning("File Error", f"{e}")
                messagebox.showinfo(
                    "Project Created", f"Project '{project_name}' has been created in {project_dir}"
                )
            else:
                messagebox.showwarning("Project Creation", "Cancelled")
def run():
    root = tk.Tk()
    root.title("Project Manager")
    pm = ProjectManagerApp(root)
    root.geometry("640x480+300+150")
    root.resizable(True, True)
    root.mainloop(),
    if __name__ == "__main__":
        run()
        self.apps: List[str] = self.load_apps()
        self.create_widgets()
        self.create_menu()
        self.bind(
            "<Configure>", lambda event, canvas=self.main_canvas: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        self.main_canvas.pack(side="left", fill="both", expand=True)

    def create_widgets(self) -> None:
        """This method creates the widgets needed for the application."""
        self.label = tk.Label(
            self.list_frame, text=f"{len(self.apps)} applications added"
        )
        self.label.pack(side="top", anchor="w")
        self.add_button = tk.Button(
            self.list_frame, text="Add Application", command=self.add_application
        )
        self.add_button.pack(side="top")
        self.clear_button = tk.Button(
            self.list_frame,
            text="Clear Applications",
            command=self.clear_applications,
        )
        self.clear_button.pack(side="bottom")
        self.listbox = tk.Listbox(
            self.list_frame, width=60, height=20, selectmode="SINGLE"
        )
        self.listbox.pack(side="top", padx=10, pady=10, fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.display_selected_app_info)

    def create_menu(self) -> None:
        """This method creates the menu for the application."""
        self.main_menu = tk.Menu(self)
        file_menu = tk.Menu(self.main_menu, tearoff=0)
        file_menu.add_command(
            label="Save Configuration", command=self.save_apps_to_file
        )
        file_menu.add_command(
            label="Load Configuration", command=self.load_apps_from_file
        )
        self.main_menu.add_cascade(label="File", menu=file_menu)
        self.main_menu.add_command(
            label="Create Project", command=self.create_project_structure
        )
        self.config(menu=self.main_menu)

    def add_application(self) -> None:
        """This method launches a file dialog to add a new application."""
        app_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select Application",
            filetypes=self.SUPPORTED_APP_FILETYPES,
        )
        if app_path and app_path not in self.apps:
            self.apps.append(app_path)
            self.listbox.insert("end", app_path)
            self.label.config(text=f"{len(self.apps)} applications added")

    def display_selected_app_info(self, event) -> None:
        """This method displays information about the selected application."""
        selected = self.listbox.get("active")
        self.logging.info(f"Selected app: {selected}")
        if selected:
            try:
                info = subprocess.check_output([selected, "--version"],
                                                stderr=subprocess.STDOUT,
                                                universal_newlines=True,
                                                timeout=5)
                messagebox.showinfo("Application Info", f"{selected}\n{info}")
            except Exception as e:
                messagebox.showwarning("Application Error", f"{e}")

    def clear_applications(self) -> None:
        """This method clears all previously added applications."""
        self.apps = []
        self.listbox.delete(0, "end")
        self.label.config(text=f"{len(self.apps)} applications added")

    def load_apps_from_file(self) -> None:
        """This method loads previous applications from a saved configuration file."""
        if self.CONFIG_FILE_PATH.exists():
            with self.CONFIG_FILE_PATH.open("r", encoding="utf-8") as f:
                try:
                    self.apps = json.load(f)
                    self.listbox.delete(0, "end")
                    for app_path in self.apps:
                        self.listbox.insert("end", app_path)
                    self.label.config(text=f"{len(self.apps)} applications added")
                except json.JSONDecodeError as e:
                    messagebox.showwarning("Configuration Error", f"{e}")

    def save_apps_to_file(self) -> None:
        """This method saves the current configuration of applications to a JSON file."""
        with self.CONFIG_FILE_PATH.open("w", encoding="utf-8") as f:
            json.dump(self.apps, f)

    def create_project_structure(self) -> None:
        """This method prompts the user for a project name and location, and creates a pre-determined directory structure for the project."""
        project_name = simpledialog.askstring(
            self.PROJECT_NAME_PROMPT, self.PROJECT_NAME_INPUT
        )
        if project_name and messagebox.askyesno(self.CONFIRMATION_TITLE, self.CONFIRMATION_TEXT):
            base_path = filedialog.askdirectory()
            if base_path:
                project_dir = pathlib.Path(base_path) / project_name
                project_dir.mkdir(parents=True, exist_ok=True)
                for folder, files in self.get_project_structure().items():
                    folder_path = project_dir / folder if folder != "root" else project_dir
                    folder_path.mkdir(parents=True, exist_ok=True)
                    for file in files:
                        file_extension = pathlib.Path(file).suffix.lower()
                        file_path = folder_path / file
                        content = FileType(file_extension).get_placeholder_content(
                            self, file_path.name
                        )
                        try:
                            file_path.write_text(content, encoding="utf-8")
                        except Exception as e:
                            self.logging.exception(f"Failed to create {file_path}: {e}")
                            messagebox.showwarning("File Error", f"{e}")
                messagebox.showinfo(
                    "Project Created", f"Project '{project_name}' has been created in {project_dir}"
                )
            else:
                messagebox.showwarning("Project Creation", "Cancelled")

    def get_project_structure(self) -> dict:
        """This method returns the default structure for a new project."""
        try:
            with open(self.RESOURCE_DIR / "project_structure.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logging.exception(f"Failed to load project structure: {e}")
            return {"root": []}

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s"
    )

    app = AppManager()
    app.mainloop()