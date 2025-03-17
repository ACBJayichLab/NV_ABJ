__all__ = ['SignalGeneratorGui']

from qtpy_files._generated_ import Ui_SignalGeneratorWindow
from PyQt5 import QtCore, QtWidgets
import sys

class SignalGeneratorGui(Ui_SignalGeneratorWindow):
    def __init__(self,window):
        self.setupUi(window)

        self.on_button.clicked.connect(self.signal_on)
        self.off_button.clicked.connect(self.signal_off)
        self.set_frequency_button.clicked.connect(self.set_frequency)
        self.set_power_button.clicked.connect(self.set_power)

    
    def signal_on(self):
        ...
    def signal_off(self):
        ...
    def set_frequency(self):
        frequency = float(self.frequency_entry.text())

    def set_power(self):
        power = float(self.power_entry.text())




if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)

    MainWindow =QtWidgets.QMainWindow()
    ui = SignalGeneratorUi(MainWindow)
    
    MainWindow.setFixedSize(230, 100)
    MainWindow.setWindowTitle('Sig Gen')

    MainWindow.show()
    app.exec()
