from abc import abstractmethod
from qudi.core import Base

class SignalGeneratorInterface(Base):
    """This is a class for a signal generator not limited to but used for control of the RF supplied to the NV and allows for a general 
    implementation for the singal frequency generators 
    """

    @property
    @abstractmethod
    def frequency_range_hz(self):
        """This is meant to take in the frequency range of the device as a tuple in Hz
        """
        ...
    
    @property
    @abstractmethod
    def power_range_dbm(self):
        """This takes in the power range of the device that you are interfacing with as a tuple in dBm
        """
        ...

    # every signal generator needs to have these commands 
    @abstractmethod
    def set_frequency_hz(self,frequency):
        """Sets a singal frequency on the device in question in Hz

        Args:
            frequency (float): no return 
        """
        pass

    @abstractmethod
    def set_power_dbm(self,power):
        """Sets the signal power in dBm 

        Args:
            power (float): no return
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
    def load_frequency_list_hz(self,frequency_list):
        """This is meant to be a command to load a frequency list to a device if the device can't do this it can be implemented using the set frequency
            and saving the list as a property to the class triggering you can just iterate through the list 
        """
        pass

    @abstractmethod
    def iterate_frequency(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        pass

