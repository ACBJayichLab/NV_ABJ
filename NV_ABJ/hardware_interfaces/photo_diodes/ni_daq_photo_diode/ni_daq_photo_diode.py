__all__ = ["NiDaqPhotoDiode"]

# National instruments imports 
import nidaqmx

# importing abstract class
from NV_ABJ.abstract_interfaces.photo_diode import PhotoDiode

class NiDaqPhotoDiode(PhotoDiode):

    def __init__(self,device_name:str,photo_diode_channel:str,conversion_function:callable):
        self.device_name = device_name
        self.photo_diode_channel = photo_diode_channel
        self.conversion_function = conversion_function

    def get_laser_power_w(self, *args,**kwargs)->float:
        """Returns the laser power of the a photo diode in watts 

        Returns:
            float: Laser power in watts
        """
        return self.conversion_function(self.read_voltage(),*args,**kwargs)

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
        

if __name__ == "__main__":
    def laser_power_func(voltage:float,x,y)->float:
        power_w =  (0.0013694017*voltage - 0.0000285044) + x+y
        return power_w
    
    green_photo_diode = NiDaqPhotoDiode(device_name="PXI1Slot5",
                                    photo_diode_channel="ai0",
                                    conversion_function=laser_power_func)



    print(green_photo_diode.read_voltage())
    print(green_photo_diode.get_laser_power_w(0,y=9)*1e3)