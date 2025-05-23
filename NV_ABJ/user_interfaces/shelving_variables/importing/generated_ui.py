# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\importing_variables_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_import_variables_widget(object):
    def setupUi(self, import_variables_widget):
        import_variables_widget.setObjectName("import_variables_widget")
        import_variables_widget.resize(208, 272)
        import_variables_widget.setMinimumSize(QtCore.QSize(208, 272))
        import_variables_widget.setMaximumSize(QtCore.QSize(208, 272))
        self.single_variables = QtWidgets.QPlainTextEdit(import_variables_widget)
        self.single_variables.setGeometry(QtCore.QRect(10, 20, 191, 121))
        self.single_variables.setMouseTracking(False)
        self.single_variables.setWhatsThis("")
        self.single_variables.setPlaceholderText("Variables to export. Comma seperated")
        self.single_variables.setObjectName("single_variables")
        self.failure_text_label = QtWidgets.QLabel(import_variables_widget)
        self.failure_text_label.setGeometry(QtCore.QRect(10, 250, 111, 16))
        self.failure_text_label.setStyleSheet("color:rgb(255, 0, 0)")
        self.failure_text_label.setObjectName("failure_text_label")
        self.import_variables_push_button = QtWidgets.QPushButton(import_variables_widget)
        self.import_variables_push_button.setGeometry(QtCore.QRect(10, 200, 191, 41))
        self.import_variables_push_button.setObjectName("import_variables_push_button")
        self.browse_button = QtWidgets.QPushButton(import_variables_widget)
        self.browse_button.setGeometry(QtCore.QRect(130, 170, 75, 23))
        self.browse_button.setObjectName("browse_button")
        self.label_3 = QtWidgets.QLabel(import_variables_widget)
        self.label_3.setGeometry(QtCore.QRect(10, 150, 101, 16))
        self.label_3.setObjectName("label_3")
        self.file_path = QtWidgets.QLineEdit(import_variables_widget)
        self.file_path.setGeometry(QtCore.QRect(10, 170, 113, 20))
        self.file_path.setReadOnly(False)
        self.file_path.setPlaceholderText("")
        self.file_path.setObjectName("file_path")
        self.label = QtWidgets.QLabel(import_variables_widget)
        self.label.setGeometry(QtCore.QRect(10, 0, 141, 20))
        self.label.setObjectName("label")

        self.retranslateUi(import_variables_widget)
        QtCore.QMetaObject.connectSlotsByName(import_variables_widget)

    def retranslateUi(self, import_variables_widget):
        _translate = QtCore.QCoreApplication.translate
        import_variables_widget.setWindowTitle(_translate("import_variables_widget", "Import"))
        self.failure_text_label.setText(_translate("import_variables_widget", "Failure Text Label"))
        self.import_variables_push_button.setText(_translate("import_variables_widget", "Import"))
        self.browse_button.setText(_translate("import_variables_widget", "Browse"))
        self.label_3.setText(_translate("import_variables_widget", "File Name"))
        self.label.setText(_translate("import_variables_widget", "Variables to Import"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    import_variables_widget = QtWidgets.QWidget()
    ui = Ui_import_variables_widget()
    ui.setupUi(import_variables_widget)
    import_variables_widget.show()
    sys.exit(app.exec_())
