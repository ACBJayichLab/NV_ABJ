__all__ = []

# Numpy is used for array allocation and fast math operations here
import numpy as np
from numpy.typing import NDArray

# National instruments imports 
import nidaqmx

# importing abstract class
from NV_ABJ.abstract_interfaces.photo_diode import PhotoDiode

class NiDaqPhotoDiode(PhotoDiode):

    def __init__(self,device_name:str,photo_diode_channel:str,conversion_factor_volts_per_watts:float):
        self.device_name = device_name
        self.photo_diode_channel = photo_diode_channel
        self.conversion_factor_volts_per_watts = conversion_factor_volts_per_watts

    def get_laser_power_w(self)->float:
        """Returns the laser power of the a photo diode in watts 

        Returns:
            float: Laser power in watts
        """
        return self.read_voltage()/self.conversion_factor_volts_per_watts 

    # This is handled by the daq
    def make_connection(self):
        pass
    
    def close_connection(self):
        pass

    def read_voltage(self):
        photo_diode_channel = self.device_name+"/"+self.photo_diode_channel

        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(photo_diode_channel)
                voltage = task.read()        

        except nidaqmx.DaqError as e:
            raise Exception(f"DAQmx error occurred: {e}")
        
        else:
            return voltage