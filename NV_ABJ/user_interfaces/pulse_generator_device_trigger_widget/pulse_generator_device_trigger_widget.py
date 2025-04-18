#############################################################################################
# Third party
from PyQt5.QtCore import QTimer

# Classes for Typing
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import SequenceDevice
from NV_ABJ.abstract_interfaces.pulse_generator import PulseGenerator
from NV_ABJ.abstract_interfaces.photo_diode import PhotoDiode
# Importing generated python code from qtpy ui
from NV_ABJ.user_interfaces.pulse_generator_device_trigger_widget.generated_ui import Ui_pulse_generator_device_trigger_widget
#############################################################################################

class PulseGeneratorTriggerWidget(Ui_pulse_generator_device_trigger_widget):

    def __init__(self,window,
                 trigger_device:SequenceDevice,
                 pulse_generator:PulseGenerator,
                 photo_diode:PhotoDiode = None,
                 pulse_generator_controlled_devices:list = None,
                 on_text:str = "Turn On",
                 off_text:str = "Turn Off",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(window)
        self._running = False



        self.trigger_device = trigger_device
        self.on_text = on_text
        self.off_text = off_text
        self.pulse_generator = pulse_generator
        if pulse_generator_controlled_devices != None:
            self.pulse_generator_controlled_devices = pulse_generator_controlled_devices
        else:
            self.pulse_generator_controlled_devices = [self.trigger_device]

        # Calling to update text this will default toggle the to be off
        self.trigger_device.device_status = True
        self.toggle_devices()

        self.toggle_push_button.clicked.connect(self.toggle_devices)

            
        if photo_diode != None:
            self.photo_diode = photo_diode
            self.timer = QTimer()   
            self.timer.timeout.connect(self.update_time)
            self.timer.start(1000)
        else:
            self.label.deleteLater()
            self.power_entry.deleteLater()


    def update_time(self):
        laser_power_mw = self.photo_diode.get_laser_power_w()*1000
        self.power_entry.setText(f"{laser_power_mw:.2e}")

    def toggle_devices(self):

        if self.trigger_device.device_status:
            self.toggle_push_button.setText(self.off_text)
            self.trigger_device.device_status = False     
        else:
            self.toggle_push_button.setText(self.on_text)     
            self.trigger_device.device_status = True

        self.pulse_generator.stop()
        self.pulse_generator.update_devices(self.pulse_generator_controlled_devices)

    def freeze_gui(self):
        """This is a function that is called to freeze the GUI when another program is running 
        """
        self.toggle_push_button.setEnabled(False)
    
    def unfreeze_gui(self): 
        """Returns control to all commands for the GUI after the programs have finished running 
        """
        self.toggle_push_button.setEnabled(True)

if __name__ == "__main__":
    from PyQt5 import QtWidgets
    import sys
    from experimental_configuration import *

    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    ui = PulseGeneratorTriggerWidget(main_window,
                                     pulse_generator=pulse_blaster,
                                     trigger_device=green_aom_trigger,
                                     photo_diode=green_photo_diode,
                                     pulse_generator_controlled_devices=[green_aom_trigger,microwave_switch_1])

    main_window.show()
    app.exec()