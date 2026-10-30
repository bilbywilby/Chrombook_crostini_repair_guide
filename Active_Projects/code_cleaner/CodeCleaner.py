import logging
import os
import shutil
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from tkinter import filedialog, messagebox
import autopep8
import configparser
import subprocess

class CodeCleaner:
    def __init__(self):
        self.config = None
        self.templates = {}
        self.logfile = f'code_clean_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'
        logging.basicConfig(filename=self.logfile, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
        self.load_config()
        self.install_package('autopep8')

    def load_config(self):
        try:
            config_path = Path('~/.config/code_cleaner/config.ini').expanduser()
            if not config_path.exists():
                logging.warning(f"The configuration file is not found at location {config_path}.")
                return
            self.config = configparser.ConfigParser()
            self.config.read(config_path)
            if 'autopep8' not in self.config.sections():
                logging.warning("The [autopep8] section is not found in the configuration file, which makes it malformed.")
                self.config = None
        except Exception as e:
            logging.error(f"There's an error loading the configuration file: {e}", exc_info=True)
            self.config = None

    def run_autopep8(self, directory):
        try:
            if not self.config:
                logging.warning("No configuration file for AutoPep8 is found. Default settings will be used.")
                result = autopep8.fix_directory(directory, options=['-a', '-j0'])
            else:
                result = autopep8.fix_directory(directory, options=['--global-config', self.config.get('autopep8', 'config_file')])
            if result:
                logging.warning("AutoPep8 detected issues and autofixed them!")
                for line in result.split('\n'):
                    logging.warning(line)
        except Exception as e:
            logging.error(f"There's an error while running AutoPep8: {e}", exc_info=True)
            raise e

    def clean_code(self, directory):
        try:
            self.run_autopep8(directory)
            output_file = f"{os.path.basename(directory)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
            with open(output_file, "w") as file:
                for path, dirs, files in os.walk(directory):
                    for file_name in files:
                        if file_name.endswith(".py"):
                            full_path = os.path.join(path, file_name)
                            with open(full_path, "r") as py_file:
                                code = py_file.read()
                            file.write(code + "\n")
            logging.info(f"The output file {output_file} has been generated at {os.path.abspath(output_file)}.")
        except Exception as e:
            logging.exception(f"There's an error while cleaning the code: {e}")
            raise e

    def select_directory(self):
        try:
            root = filedialog.Tk()
            root.title('Select Directory')
            frame = ttk.Frame(root)
            frame.pack(padx=10, pady=10)
            label = ttk.Label(frame, text="Select a folder containing Python source codes:")
            label.grid(padx=5, pady=5)
            self.dir_entry = ttk.Entry(frame)
            self.dir_entry.grid(padx=5, pady=5, columnspan=3)

            def on_select_folder():
                selected_folder = filedialog.askdirectory()
                self.dir_entry.delete(0, tk.END)
                self.dir_entry.insert(0, selected_folder)

            browse_button = ttk.Button(frame, text="Browse...", command=on_select_folder)
            browse_button.grid(padx=5)
            root.mainloop()
            return self.dir_entry.get(), None

        except Exception as e:
            logging.error(f"Error while selecting directory: {e}", exc_info=True)
            raise e

    def clean_button_clicked(self):
        try:
            project_dir = self.select_directory()
            self.clean_code(project_dir)
            messagebox.showinfo("Code Cleanup", f"The code has been successfully cleaned. The output file has been generated at {os.path.abspath(project_dir)}.")
        except ValueError as e:
            logging.error(f"ValueError: {e}")
            messagebox.showerror("Error", "Failed to clean the code. No directory is selected.")
        except Exception as e:
            logging.exception(f"There's an error while cleaning the code: {e}")
            messagebox.showerror("Error", "Failed to clean the code. Check the log file for details.")

    def run_gui(self):
        try:
            root = tk.Tk()
            root.geometry("300x50")
            root.resizable(0, 0)
            root.title("Clean Code")
            clean_button = tk.Button(root, text="Select Directory to Clean", width=25, command=self.clean_button_clicked)
            clean_button.pack(pady=10)
            root.mainloop()
        except Exception as e:
            logging.error(f"Error while running GUI: {e}", exc_info=True)
            raise e

    def install_package(self, package):
        try:
            if package not in sys.modules:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        except Exception as e:
            logging.error(f"There's an error installing the package: {e}", exc_info=True)
            raise e

def main():
    try:
        code_cleaner = CodeCleaner()
        code_cleaner.run_gui()
    except Exception as e:
        logging.exception(f"There's an error running the program: {e}", exc_info=True)
        raise e

if __name__ == "__main__":
    main()