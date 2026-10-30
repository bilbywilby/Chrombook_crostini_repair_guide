import logging
import tkinter as tk
import tkinter.messagebox as messagebox
import pickle


class ToDoListApp(tk.Tk):

    # Constants for widget dimensions, fonts, and colors
    WINDOW_TITLE = "To-Do List App"
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 400
    ENTRY_FONT = ("Arial", 14)
    LIST_FONT = ("Courier", 14)
    BG_COLOR = "#f0f0f0"
    BUTTON_COLOR = "#d1d1d1"

    def __init__(self):
        super().__init__()
        self.title(self.WINDOW_TITLE)
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.configure(bg=self.BG_COLOR)
        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        # Create a frame to hold the widgets
        frame = tk.Frame(self, bg=self.BG_COLOR)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create a label widget for the title
        title_label = tk.Label(frame, text="To-Do List", font=("Arial", 24, "bold"), bg=self.BG_COLOR)
        title_label.pack(pady=20)

        # Create a listbox widget to display the tasks
        listbox_frame = tk.Frame(frame, bg=self.BG_COLOR)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        listbox_label = tk.Label(listbox_frame, text="TASK LIST", font=self.LIST_FONT, bg=self.BG_COLOR)
        listbox_label.pack(pady=10)

        self.listbox = tk.Listbox(listbox_frame, height=12, width=40, font=self.LIST_FONT)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar widget to scroll the listbox
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Create an entry widget to enter a task
        entry_frame = tk.Frame(frame, bg=self.BG_COLOR)
        entry_frame.pack(fill=tk.X, padx=20, pady=10)

        entry_label = tk.Label(entry_frame, text="TASK NAME", font=self.LIST_FONT, bg=self.BG_COLOR)
        entry_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(entry_frame, font=self.ENTRY_FONT, width=30)
        self.entry.pack(side=tk.LEFT, padx=(10, 0))

        # Create a button frame to hold the add/delete buttons
        button_frame = tk.Frame(frame, bg=self.BG_COLOR)
        button_frame.pack(pady=20)

        # Create a button widget to add a task
        add_button = tk.Button(button_frame, text="+ ADD TASK", bg=self.BUTTON_COLOR, font=self.LIST_FONT, command=self._add_task)
        add_button.pack(side=tk.LEFT, padx=10)

        # Create a button widget to delete a task
        delete_button = tk.Button(button_frame, text="- DELETE TASK", bg=self.BUTTON_COLOR, font=self.LIST_FONT, command=self._delete_task)
        delete_button.pack(side=tk.LEFT, padx=10)

    def _load_data(self):
        try:
            with open("todo_list.pkl", "rb") as f:
                data = pickle.load(f)
                self.listbox.insert(tk.END, *data)
                logging.info(f"Successfully loaded {len(data)} tasks")
        except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
            logging.warning(f"Failed to load data: {str(e)}")

    def _save_data(self):
        data = self.listbox.get(0, tk.END)
        try:
            with open("todo_list.pkl", "wb") as f:
                pickle.dump(data, f)
                logging.info(f"Successfully saved {len(data)} tasks")
        except (FileNotFoundError, pickle.PickleError) as e:
            logging.error(f"Failed to save data: {str(e)}")

    def _add_task(self):
        new_task = self.entry.get().strip()
        if new_task:
            self.listbox.insert(tk.END, new_task)
            self.entry.delete(0, tk.END)
            self._save_data()

    def _delete_task(self):
        selection = self.listbox.curselection()
        if selection:
            task = self.listbox.get(selection)
            confirm = messagebox.askyesno("Task Deletion", f"Are you sure to delete '{task}'?")
            if confirm:
                self.listbox.delete(selection)
                self._save_data()


if __name__ == "__main__":
    logging.basicConfig(filename="todo_list.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    app = ToDoListApp()
    app.mainloop()