#############################################################################################
# Third party
from PyQt5.QtCore import QTimer

# Classes for Typing
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import SequenceDevice
from NV_ABJ.abstract_interfaces.pulse_generator import PulseGenerator
from NV_ABJ.abstract_interfaces.photo_diode import PhotoDiode
# Importing generated python code from qtpy ui
from NV_ABJ.user_interfaces.aom_trigger_widget.generated_ui import Ui_AomTrigger
#############################################################################################

class AomTriggerWidget(Ui_AomTrigger):

    def __init__(self,window,photo_diode:PhotoDiode,
                 aom_trigger_device:SequenceDevice,
                 pulse_generator:PulseGenerator,
                 aom_on_text:str = "Turn On AOM",
                 aom_off_text:str = "Turn Off AOM",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(window)

        self.photo_diode = photo_diode
        self.aom_trigger_device = aom_trigger_device
        self.aom_on_text = aom_on_text
        self.aom_off_text = aom_off_text
        self.pulse_generator = pulse_generator

        self.toggle_aom_push_button.setText(self.aom_off_text) 
        self.toggle_aom_push_button.clicked.connect(self.toggle_aom)
        # Calling AOM to update text
        self.toggle_aom()
            

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time() 

    def update_time(self):
        laser_power_mw = self.photo_diode.get_laser_power_w()/1000
        self.aom_power_entry.setText(str(laser_power_mw))

    def toggle_aom(self):

        if self.aom_trigger_device.device_status:
            self.toggle_aom_push_button.setText(self.aom_off_text)
            self.aom_trigger_device.device_status = False     
        else:
            self.toggle_aom_push_button.setText(self.aom_on_text)     
            self.aom_trigger_device.device_status = True
        self.pulse_generator.stop()
        self.pulse_generator.update_devices([self.aom_trigger_device])
