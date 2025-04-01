from PyQt5 import QtCore, QtWidgets
import sys

class Ui_SignalGeneratorWindow(object):
    def setupUi(self, SignalGeneratorWindow):
        SignalGeneratorWindow.setObjectName("SignalGeneratorWindow")
        SignalGeneratorWindow.resize(230, 100)
        self.on_button = QtWidgets.QPushButton(SignalGeneratorWindow)
        self.on_button.setGeometry(QtCore.QRect(10, 10, 75, 23))
        self.on_button.setObjectName("on_button")
        self.off_button = QtWidgets.QPushButton(SignalGeneratorWindow)
        self.off_button.setGeometry(QtCore.QRect(90, 10, 75, 23))
        self.off_button.setObjectName("off_button")
        self.label = QtWidgets.QLabel(SignalGeneratorWindow)
        self.label.setGeometry(QtCore.QRect(20, 40, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(SignalGeneratorWindow)
        self.label_2.setGeometry(QtCore.QRect(20, 70, 81, 16))
        self.label_2.setObjectName("label_2")
        self.frequency_entry = QtWidgets.QLineEdit(SignalGeneratorWindow)
        self.frequency_entry.setGeometry(QtCore.QRect(110, 40, 61, 20))
        self.frequency_entry.setObjectName("frequency_entry")
        self.power_entry = QtWidgets.QLineEdit(SignalGeneratorWindow)
        self.power_entry.setGeometry(QtCore.QRect(110, 70, 61, 20))
        self.power_entry.setObjectName("power_entry")
        self.set_frequency_button = QtWidgets.QPushButton(SignalGeneratorWindow)
        self.set_frequency_button.setGeometry(QtCore.QRect(180, 40, 41, 23))
        self.set_frequency_button.setObjectName("set_frequency_button")
        self.set_power_button = QtWidgets.QPushButton(SignalGeneratorWindow)
        self.set_power_button.setGeometry(QtCore.QRect(180, 70, 41, 23))
        self.set_power_button.setObjectName("set_power_button")

        self.retranslateUi(SignalGeneratorWindow)
        QtCore.QMetaObject.connectSlotsByName(SignalGeneratorWindow)

    def retranslateUi(self, SignalGeneratorWindow):
        _translate = QtCore.QCoreApplication.translate
        SignalGeneratorWindow.setWindowTitle(_translate("SignalGeneratorWindow", "Dialog"))
        self.on_button.setText(_translate("SignalGeneratorWindow", "Turn On"))
        self.off_button.setText(_translate("SignalGeneratorWindow", "Turn Off"))
        self.label.setText(_translate("SignalGeneratorWindow", "Frequency(MHz)"))
        self.label_2.setText(_translate("SignalGeneratorWindow", "Power (dBm)"))
        self.set_frequency_button.setText(_translate("SignalGeneratorWindow", "Set"))
        self.set_power_button.setText(_translate("SignalGeneratorWindow", "Set"))

class PhotonCounterGui(Ui_SignalGeneratorWindow):
    def __init__(self,window,SignalGeneratorInterface):

        self.SignalGeneratorInterface = SignalGeneratorInterface
        self.setupUi(window)

        self.on_button.clicked.connect(self.SignalGeneratorInterface.turn_on_signal)
        self.off_button.clicked.connect(self.SignalGeneratorInterface.turn_off_signal)
        self.set_frequency_button.clicked.connect(self.setting_frequency)
        self.set_power_button.clicked.connect(self.setting_power)
    
    def setting_frequency(self):
        # self.SignalGeneratorInterface.set_frequency_hz(
        try:
            frequency = int(float(self.frequency_entry.text())*pow(10,6))
            self.SignalGeneratorInterface.set_frequency_hz(frequency)
            print(frequency)
        except:
            pass

        
   
    def setting_power(self):
        self.SignalGeneratorInterface.set_power_dbm(float(self.power_entry.text()))

if __name__ == "__main__":

    from NV_ABJ import SG380

    SignalGeneratorInterface = SG380.make_gpib_connection(gpib_identification='GPIB0::27::INSTR')
    
    app = QtWidgets.QApplication(sys.argv)

    MainWindow =QtWidgets.QMainWindow()
    ui = SignalGeneratorGui(MainWindow,SignalGeneratorInterface)
    
    MainWindow.setFixedSize(230, 100)
    MainWindow.setWindowTitle('Sig Gen')

    MainWindow.show()
    app.exec()
