import os
import tkinter as tk
from typing import List, Tuple


class ProjectCreatorGUI:
    """
    This class creates a graphical user interface for selecting a template and project directory,
    then proceeds to create a project based on the selected template.
    """

    def __init__(self, master: tk.Tk) -> None:
        """
        Initializes the ProjectCreatorGUI class.

        :param master: The root window for the graphical user interface.
        """
        self.master = master
        self.master.title('Project Creator')
        self.project_path = None
        self.template_path = None


        self.template_handler = None
        self.select_template_btn = None
        self.template_path_lbl = None
        self.select_project_btn = None
        self.project_path_lbl = None
        self.create_project_btn = None




        self.status_lbl = None
        self.organize_widgets()

    def organize_widgets(self) -> None:
        """
        Organizes all the widgets.
        """
        self.select_template_btn = tk.Button(
            self.master,

            text='Select Template',





            command=self.select_template,
            font=('Helvetica', 12),
        )
        self.select_template_btn.pack(pady=10)

        self.template_path_lbl = tk.Label(
            self.master,




            text='No template selected.',
            font=('Helvetica', 12)
        )
        self.template_path_lbl.pack()

        self.select_project_btn = tk.Button(
            self.master,
            text='Select Project Directory',




            command=self.select_project_directory,
            font=('Helvetica', 12),
        )
        self.select_project_btn.pack(pady=10)

        self.project_path_lbl = tk.Label(
            self.master,




            text='No project directory selected.',
            font=('Helvetica', 12)
        )
        self.project_path_lbl.pack()

        self.create_project_btn = tk.Button(
            self.master,




            text='Create Project',
            command=self.create_project,
            font=('Helvetica', 12, 'bold'),
        )
        self.create_project_btn.pack(pady=10)

        self.status_lbl = tk.Label(








            self.master,





            text='Ready',
            font=('Helvetica', 12)
        )
        self.status_lbl.pack()

    def select_template(self) -> None:
        """
        Opens a dialog box for the user to select a template and updates the template path label.
        """


        self.template_path = tk.filedialog.askopenfilename(title='Select Template')
        self.template_path_lbl.config(text=self.template_path)

    def select_project_directory(self) -> None:
        """




        Opens a dialog box for the user to select a project directory and updates the
        project directory path label.
        """


        self.project_path = tk.filedialog.askdirectory(title='Select Project Directory')
        self.project_path_lbl.config(text=self.project_path)

    def create_project(self) -> None:
        """
        Creates a project using the user-selected template and directory.
        """
        if not self.check_inputs():
            return

        # Reads the template file structure.
        try:
            with open(self.template_path, 'r', encoding='utf-8') as file:
                file_structure = file.read()
        except Exception as e:
            self.set_status(f'Error: failed while reading template file {self.template_path}.\n{e}')
            return

        self.template_handler = TemplateHandler(file_structure)
        self.template_handler.check_placeholders(self.project_path)

        try:
            self.template_handler.create_structure()
        except Exception as e:
            self.set_status(f'Error: failed while creating project structure.\n{e}')
            return

        self.set_status('Project created successfully.')

    def check_inputs(self) -> bool:
        """
        Validates the input fields.

        :return: True if the template and project directory fields are valid.
        """
        if not self.template_path or not os.path.exists(self.template_path):
            self.set_status('Error: No template selected.')
            return False

        if not self.project_path or not os.path.exists(self.project_path):
            self.set_status('Error: No project directory selected.')
            return False

        if not os.path.isfile(self.template_path) or not os.path.splitext(self.template_path)[1]:
            self.set_status('Error: Invalid template file.')
            return False

        return True



    def set_status(self, message: str) -> None:
        """
        Sets the value of the status label.

        :param message: The message to set in the label.
        """
        self.status_lbl.config(text=message)




class TemplateHandler:
    """
    Handles placeholders in the template for project and path as well as directory and file creation.
    """



    def __init__(self, file_structure: str) -> None:
        """
        :param file_structure: The contents of the file structure or template to process.
        """
        self.project_path = None
        self.file_structure = file_structure.strip()
        self.file_paths = self.file_structure.split('\n')

    def check_placeholders(self, project_path: str) -> None:
        """
        Replace the placeholders for project and path in the file structure.

        :param project_path: The project directory path selected by the user.
        """
        self.project_path = project_path.strip()
        self.file_paths = [path.replace('EZ_PIC', self.project_path) for path in self.file_paths]

    def create_structure(self) -> None:
        """
        Creates the project structure by creating files and directories in the specified project directory.
        """
        for file_path in self.file_paths:
            path, is_file = self.check_path(file_path)



            if path in ['', '.']:
                continue



            try:
                if is_file:
                    with open(path, 'w', encoding='utf-8'):


                        pass
                else:


                    os.makedirs(path, exist_ok=True)
            except Exception as e:
                raise Exception(f'Error while creating path {path}\n{e}')



    def check_path(self, file_path: str) -> Tuple[str, bool]:
        """
        Convert the provided template file into a path usable by the OS.

        :param file_path: The path taken from the file structure or template.
        :return: A tuple containing the path and a flag indicating if it is a file or directory.
        """
        path = file_path.replace('/', os.path.sep).replace('\\', os.path.sep)
        path = os.path.join(self.project_path, path)



        if path.endswith(os.path.sep):
            return path[:-1], False
        return path, True



if __name__ == '__main__':
    root = tk.Tk()
    app = ProjectCreatorGUI(root)
    root.mainloop()