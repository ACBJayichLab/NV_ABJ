from abc import ABCMeta, abstractmethod
from NV_ABJ import ConnectedDevice

class SignalGeneratorHardwareFormat(ConnectedDevice,metaclass=ABCMeta):
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
    @abstractmethod
    def get_frequency_hz(self):
        """Returns the frequency of the signal generator in Hz
        """
        ...
    @abstractmethod
    def get_power_dbm(self):
        """Returns the power of the signal generator in dBm
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
    def get_frequency_list_hz(self):
        """returns the frequency list currently loaded 
        """
        ...

    @abstractmethod
    def iterate_frequency(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        pass

class SignalGeneratorInterface(SignalGeneratorHardwareFormat):
    """This is a class for a signal generator not limited to but used for control of the RF supplied to the NV and allows for a general 
    implementation for the singal frequency generators 
    """

    def __init__(self,_device_configuration_class, _device_hardware_class):
        self._device_configuration_class = _device_configuration_class
        self._device_hardware_class = _device_hardware_class

    @property
    def device_configuration_class(self):
        return self._device_configuration_class
    @property
    def device_hardware_class(self):
        return self._device_hardware_class

    def make_connection(self):
        self.device_hardware_class(self.device_configuration_class).make_connection()

    def close_connection(self):
        self.device_hardware_class(self.device_configuration_class).close_connection()

    @property
    def frequency_range_hz(self):
        """This is meant to take in the frequency range of the device as a tuple in Hz
        """
        return self.device_hardware_class(self.device_configuration_class).frequency_range_hz
    
    @property
    def power_range_dbm(self):
        """This takes in the power range of the device that you are interfacing with as a tuple in dBm
        """
        return self.device_hardware_class(self.device_configuration_class).power_range_dbm

    # every signal generator needs to have these commands 
    def set_frequency_hz(self,frequency):
        """Sets a singal frequency on the device in question in Hz

        Args:
            frequency (float): no return 
        """
        self.device_hardware_class(self.device_configuration_class).set_frequency_hz(frequency)


    def set_power_dbm(self,power):
        """Sets the signal power in dBm 

        Args:
            power (float): no return
        """
        self.device_hardware_class(self.device_configuration_class).set_power_dbm(power)
   
    def get_power_dbm(self):
        """Returns the signal generators power in dBm
        """
        return self.device_hardware_class(self.device_configuration_class).get_power_dbm()
    
    def get_frequency_hz(self):
        """Returns the signal generators power in dBm
        """
        return self.device_hardware_class(self.device_configuration_class).get_frequency_hz()
    
    def turn_on_signal(self):
        """Turns on the signal source this will map to the specific port in question
          and does not turn on the device just the signal
        """
        self.device_hardware_class(self.device_configuration_class).turn_on_signal()

    def turn_off_signal(self):
        """This turns off the signal source and will not turn off the device 
        """
        self.device_hardware_class(self.device_configuration_class).turn_off_signal()
    
    # these will likely be compound commands  
    def load_frequency_list_hz(self,frequency_list):
        """This is meant to be a command to load a frequency list to a device if the device can't do this it can be implemented using the set frequency
            and saving the list as a property to the class triggering you can just iterate through the list 
        """
        self.device_hardware_class(self.device_configuration_class).load_frequency_list_hz(frequency_list)
    
    def get_frequency_list_hz(self):
        """Returns the currently loaded list of frequencies 
        """
        return self.device_hardware_class(self.device_configuration_class).get_frequency_list_hz()

    def iterate_frequency(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        self.device_hardware_class(self.device_configuration_class).iterate_frequency()
