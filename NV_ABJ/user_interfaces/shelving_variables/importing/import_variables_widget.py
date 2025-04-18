#############################################################################################
# Third party
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import os
import shelve

from generated_ui import Ui_import_variables_widget
#############################################################################################

class ImportingVariablesWidget(Ui_import_variables_widget):

    def __init__(self,window,
                 importable_variables:dict[str,callable],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(window)
        self.importable_variables = importable_variables

        # Connecting Buttons
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.import_variables_push_button.clicked.connect(self.import_shelve_variables)
        
        # Entering Variables that can be saved
        entry_text = str(self.importable_variables.keys()).replace("dict_keys([","").replace("])","").replace(", ",",\n").replace("'","")
        self.single_variables.setPlainText(entry_text)
        self.failure_text_label.setText("")




    def open_file_dialog(self):
        filename,_ = QFileDialog.getOpenFileName()
        if filename:
            path = Path(filename)
            self.file_path.setText(str(path))
    
    def import_shelve_variables(self):
        # Save Data

        file_path = self.file_path.text()
        reversed_file_path = file_path[::-1]
        reversed_file_path = reversed_file_path.replace("tad.","",1).replace("kab.","",1).replace("rid.","",1)
        file_path = reversed_file_path[::-1]

        print(file_path)
        # Getting Variables 
        # Making a set and then a list removes any duplicate values 
        variables_to_import = list(set(self.single_variables.toPlainText().replace("\n","").split(",")))

        # Removing any blanks
        temp_variables_to_import = []
        for var in variables_to_import:
            if var != "":
                temp_variables_to_import.append(var)
        variables_to_import = temp_variables_to_import

        # Checking for valid variables 
        for variable in variables_to_import:
            if variable not in self.importable_variables:
                self.failure_text_label.setText(f"No Variable Named: {variable}")
                return
        # Removing error message
        self.failure_text_label.setText(f"")
        import_warning_text = "Did not import:"
        # Saving variables if no issues present
        with shelve.open(file_path, 'r') as db:

            for variable in variables_to_import:
                try:
                    self.importable_variables[variable](db[variable])
                except:
                    pass
      
if __name__ == "__main__":
    from PyQt5 import QtWidgets
    import sys
    from experimental_configuration import *

    file_path = r"C:\Users\LTSPM2\Documents\GitHub\LTSPM2_Interfaces\UI_ShelvedVariables.db.dat"

    app = QtWidgets.QApplication(sys.argv)

    def print_larger(x):
        print(x*1e9)
    variables ={
        "x_position_um":print_larger,
        "y_position_um":print_larger,
        "z_position_um":print_larger
    }

    main_window = QtWidgets.QMainWindow()
    ui = ImportingVariablesWidget(main_window,
                                  importable_variables=variables)

    main_window.show()
    app.exec()