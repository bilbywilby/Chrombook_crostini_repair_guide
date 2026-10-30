def convert_to_executable(python_script_path: str) -> Optional[str]:
    """
    Convert a Python script to an executable file.

    :param python_script_path: The path of the Python script file to be converted.
    :return: The path of the converted executable file, or None if the function call fails.
    """
    if not python_script_path.endswith('.py'):
        messagebox.showerror("Error", "The file must be a Python script with a .py extension.")
      import time
def convert_to_executable(python_script_path: str) -> Optional[str]:
    """
    Convert a Python script to an executable file.

    :param python_script_path: The path of the Python script file to be converted.
    :return: The path of the converted executable file, or None if the function call fails.
    """
    if not python_script_path.endswith('.py'):
        messagebox.showerror("Error", "The file must be a Python script with a .py extension.")
        return None

    try:
        start_time = time.perf_counter()
        subprocess.check_call(['pyinstaller', '--onefile', python_script_path])
        end_time = time.perf_counter()

        executable_name = os.path.splitext(os.path.basename(python_script_path))[0] + '.exe'
        executable_path = os.path.join(os.path.dirname(python_script_path), 'dist', executable_name)

        if os.path.isfile(executable_path):
            messagebox.showinfo("Success", "The Python script was successfully converted to an executable file.")
            print(f'Time elapsed for creating executable: {end_time - start_time:.2f} seconds')
            return executable_path
        else:
            messagebox.showerror("Error", "Failed to locate the executable file.")
            return None
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to create the .exe file:{str(e)}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"{str(e)}")
        return None
start = time.perf_counter()

# Run pyinstaller to create an executable
subprocess.check_call(['pyinstaller', '--onefile', file_path])

end = time.perf_counter()
print(f'Time elapsed for creating executable: {end - start:.2f} seconds')  return None

    try:
        start_time = time.perf_counter()
        subprocess.check_call(['pyinstaller', '--onefile', python_script_path])
        end_time = time.perf_counter()

        executable_name = os.path.splitext(os.path.basename(python_script_path))[0] + '.exe'
        executable_path = os.path.join(os.path.dirname(python_script_path), 'dist', executable_name)

        if os.path.isfile(executable_path):
            messagebox.showinfo("Success", "The Python script was successfully converted to an executable file.")
            print(f'Time elapsed for creating executable: {end_time - start_time:.2f} seconds')
            return executable_path
        else:
            messagebox.showerror("Error", "Failed to locate the executable file.")
            return None
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to create the .exe file:{str(e)}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"{str(e)}")
        return None
    class Application(tk.Tk):
    """
    A simple Tkinter application for creating an executable file for a Python script file.
    """

    def __init__(self):
        super().__init__()
        self.title("Python Script to Executable")
        self.geometry("")
        self.python_script_path = ""
        self.destination_folder = ""
        self.create_widgets()

    def create_widgets(self):
        # Select File Button
        self.select_file_btn = tk.Button(self, text="Select Python Script", command=self.select_file)
        self.select_file_btn.pack(pady=10)

        # Destination Folder Button
        self.select_folder_btn = tk.Button(self, text="Select Destination Folder", command=self.select_folder)
        self.select_folder_btn.pack(pady=10)

        # Create Executable Button
        self.create_exe_btn = tk.Button(self, text="Create Executable", command=self.create_exe)
        self.create_exe_btn.pack(pady=10)

    def select_file(self):
        self.python_script_path = filedialog.askopenfilename(
            title="Select Python Script",
            filetypes=[("Python files", "*.py")]
        )

    def select_folder(self):
        self.destination_folder = filedialog.askdirectory()

    def create_exe(self):
        if not self.python_script_path:
            messagebox.showerror("Error", "Please select a Python script file.")
            return

        if not self.destination_folder:
            messagebox.showerror("Error", "Please select a destination folder.")
            return

        destination_path = os.path.join(self.destination_folder, 'output.exe')
        exe_path = convert_to_executable(self.python_script_path)

        if exe_path is None:
            messagebox.showerror("Error", "Failed to create the executable file.")
        elif os.path.isfile(destination_path):
            messagebox.showerror("Error", f"The file already exists at destination: {destination_path}")
        else:
            shutil.move(exe_path, destination_path)
            messagebox.showinfo("Success", "The Python script is successfully converted to an executable file.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()