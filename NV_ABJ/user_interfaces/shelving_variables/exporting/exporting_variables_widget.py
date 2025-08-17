#############################################################################################
# Third party
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import os
import shelve

from NV_ABJ.user_interfaces.shelving_variables.exporting.generated_ui import Ui_exporting_variables
#############################################################################################

class ExportingVariablesWidget(Ui_exporting_variables):

    def __init__(self,window,
                 savable_variables:dict,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(window)
        self.savable_variables = savable_variables

        # Connecting Buttons
        self.browse_button.clicked.connect(self.open_dir_dialog)
        self.export_variables_push_button.clicked.connect(self.shelve_variables)
        # Setting Current Folder as Location
        current_directory_os = os.getcwd()
        self.folder_location.setText(str(current_directory_os))

        # Entering Variables that can be saved
        entry_text = str(self.savable_variables.keys()).replace("dict_keys([","").replace("])","").replace(", ",",\n").replace("'","")
        self.single_variables_to_shelve.setPlainText(entry_text)
        self.failure_text_label.setText("")




    def open_dir_dialog(self):
        dir_name = QFileDialog.getExistingDirectory()
        if dir_name:
            path = Path(dir_name)
            self.folder_location.setText(str(path))
    
    def shelve_variables(self):
        # Save Data
        folder_name = self.folder_location.text()
        file_name = str(self.file_name.text()+".db")
        file_path = os.path.join(folder_name,file_name)

        # Getting Variables 
        # Making a set and then a list removes any duplicate values 
        variables_to_save = list(set(self.single_variables_to_shelve.toPlainText().replace("\n","").split(",")))

        # Removing any blanks
        temp_variables_to_save = []
        for var in variables_to_save:
            if var != "":
                temp_variables_to_save.append(var)
        variables_to_save = temp_variables_to_save

        # Checking for valid variables 
        for variable in variables_to_save:
            if variable not in self.savable_variables:
                self.failure_text_label.setText(f"No Variable Named: {variable}")
                return
        # Removing error message
        self.failure_text_label.setText(f"")
        export_text = "Failed to export:"
        failed_export = False
        # Saving variables if no issues present
        try:
            with shelve.open(file_path) as db:
                db.clear() # Removing previous implementations 
                for variable in variables_to_save:
                    try:
                        db[variable] = self.savable_variables[variable]
                    except:
                        export_text = export_text + f"{variable}, "
                        failed_export = True
            if failed_export:
                self.failure_text_label.setText(export_text)
        except:
            self.failure_text_label.setText(f"Could not export file")