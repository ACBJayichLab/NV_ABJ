from abc import ABCMeta, abstractmethod
from NV_ABJ import ConnectedDevice

class MicrowaveSource(ConnectedDevice,metaclass=ABCMeta):
    """This is a class for a signal generator not limited to but used for control of the RF supplied to the NV and allows for a general 
    implementation for the singal frequency generators 
    """

    @property
    @abstractmethod
    def frequency_range_hz(self)->tuple[float,float]:
        """This is meant to take in the frequency range of the device as a tuple in Hz
        """
        ...
    
    @property
    @abstractmethod
    def power_range_dbm(self)->tuple[float,float]:
        """This takes in the power range of the device that you are interfacing with as a tuple in dBm
        """
        ...
    @abstractmethod
    def get_frequency_hz(self)->int:
        """Returns the frequency of the signal generator in Hz
        """
        ...
    @abstractmethod
    def get_power_dbm(self)->float:
        """Returns the power of the signal generator in dBm
        """
        ...

    # every signal generator needs to have these commands 
    @abstractmethod
    def generate_sine_wave_hz_dbm(self,frequency:int,amplitude:float,*args,**kwargs):
        """Sets a singal frequency on the device in question in Hz

        Args:
            frequency (float): no return 
        """
        pass

    @abstractmethod
    def set_power_dbm(self,power:float):
        """Sets the signal power in dBm 

        Args:
            power (float): no return
        """
        pass

    @abstractmethod
    def set_frequency_hz(self,frequency_hz:int):
        """Sets the signal frequency in hz

        Args:
            frequency_hz (float): no return
        """
        pass

    @abstractmethod
    def turn_on_signal(self):
        """Turns on the signal source this will map to the specific port in question
          and does not turn on the device just the signal
        """
        pass

    @abstractmethod
    def turn_off_signal(self):
        """This turns off the signal source and will not turn off the device 
        """
        pass 
    
    # these will likely be compound commands  
    @abstractmethod
    def load_frequency_list_hz(self,frequency_list:list):
        """This is meant to be a command to load a frequency list to a device if the device can't do this it can be implemented using the set frequency
            and saving the list as a property to the class triggering you can just iterate through the list 
        """
        pass
    @abstractmethod
    def get_frequency_list_hz(self)->list:
        """returns the frequency list currently loaded 
        """
        ...

    @abstractmethod
    def iterate(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        pass
