#!/usr/bin/env python
import logging
import os
import shutil
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from tkinter import filedialog, messagebox
import configparser
import autopep8
import subprocess

class CodeCleaner:
    def __init__(self):
        self.config = None
        self.templates = {}
        self.logfile = f'code_clean_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'

        logging.basicConfig(
            filename=self.logfile,
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

        self.load_config()
        self.install_package('autopep8')

    def load_config(self):
        try:
            config_path = Path('~/.config/code_cleaner/config.ini').expanduser()

            if not config_path.exists():
                logging.warning(f"Configuration file is not found at {config_path}.")
                return

            self.config = configparser.ConfigParser()
            self.config.read(config_path)

            if 'autopep8' not in self.config.sections():
                logging.warning(f"[autopep8] section is not found in the configuration file, making it malformed.")
                self.config = None

        except Exception as e:
            logging.error(f"There's an error in loading the configuration file: {e}", exc_info=True)
            self.config = None

    def run_autopep8(self, directory):
        try:
            if not self.config:
                logging.warning("No configuration file for AutoPep8 is found. Default settings will be used.")
                result = autopep8.fix_directory(directory, options=['-a', '-j0'])
            else:
                result = autopep8.fix_directory(directory, options=['--global-config', self.config.get('autopep8', 'config_file')])

            if result:
                logging.warning("AutoPep8 detected issues and auto-fixed them!")
                for line in result.split('\n'):
                    logging.warning(line)

        except Exception as e:
            logging.error(f"There's an error while running AutoPep8: {e}", exc_info=True)
            return False

        logging.info("Code is cleaned now.")
        return True

    def clean_code(self, directory):
        if not self.run_autopep8(directory):
            logging.warning("Failed to run AutoPep8.")
            return

        output_file = f"{os.path.basename(directory)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"

        with open(output_file, "w") as file:
            for path, dirs, files in os.walk(directory):
                for file_name in files:
                    if file_name.endswith(".py"):
                        full_path = os.path.join(path, file_name)
                        with open(full_path, "r") as py_file:
                            code = py_file.read()
                        file.write(code + "\n")

        logging.info(f"Output file {output_file} is generated at location {os.path.abspath(output_file)}.")

    def select_directory(self):
        root = tk.Tk()
        root.withdraw()
        project_dir = filedialog.askdirectory(title="Select the project directory")
        root.destroy()

        if not project_dir:
            raise ValueError("No directory is selected.")

        return Path(project_dir).resolve()

    def clean_button_clicked(self):
        try:
            project_dir = self.select_directory()
            self.clean_code(project_dir)
            messagebox.showinfo("Code Cleanup", f"Code has been cleaned successfully. The output file has been generated at {os.path.abspath(project_dir)}.")
        except ValueError as e:
            logging.error(f"ValueError: {e}")
            messagebox.showerror("Error", "Failed to clean the code. No directory is selected.")
        except Exception as e:
            logging.exception(f"There's an error while cleaning the code: {e}")
            messagebox.showerror("Error", "Failed to clean the code. Check the log file for details.")

    def run_gui(self):
        root = tk.Tk()
        root.geometry("300x50")
        root.resizable(0, 0)
        root.title("Clean Code")

        clean_button = tk.Button(root, text="Select Directory to Clean", width=25, command=self.clean_button_clicked)
        clean_button.pack(pady=10)

        root.mainloop()

    def install_package(self, package):
        if package not in sys.modules:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

            except subprocess.CalledProcessError as e:
                logging.error(f"There's an error in installing the package: {e}")

def main():
    code_cleaner = CodeCleaner()
    code_cleaner.run_gui()

if __name__ == "__main__":
    main()