# importing third party modules 
import pyvisa
from dataclasses import dataclass

from NV_ABJ import SignalGeneratorHardwareFormat

@dataclass
class ConfigurationSG380:
    """This is where the constraints for connecting to the correct signal generator are stored such as the address and if we want to use the n_type_port

    Args:
        gpib_address: str = The address that you connect to the srs with
        use_n_type_port: bool = If you intend to use the N Type port(True) or the BNC(False). defaults to True 
    """
    gpib_address: str
    use_n_type_port: bool = True
    # These shouldn't be interfaced by the user and will be created on device creation and overwritten if defined 
    _frequency_range_hz: tuple = None
    _power_range_dbm:tuple = None
    _rm = None
    _srs = None

class SG380(SignalGeneratorHardwareFormat):
    """This is a implementation for the Stanford Research Instruments signal generation 
    """

    def __init__(self,device_configuration=None):
        """
        """
        if device_configuration == None:
            raise Exception("Please enter this class using the with protocol or make connection")
        else:
            self._device_configuration = device_configuration

    @property
    def device_configuration_class(self):
        return self._device_configuration

    def make_connection(self):
        
        # Takes a daq card id, daq channel, and a gpib id and returns a class to control the srs
        _rm = pyvisa.ResourceManager()
        _srs = _rm.open_resource(self._device_configuration.gpib_address)

        # Clear status
        _srs.write("*CLS")

        # Check model number from ID 
        response = str(_srs.query("*IDN?"))

        if self._device_configuration.use_n_type_port:
            if "SG382" in response:
                    freq_range = (950*pow(10,3),2.025*pow(10,9))
                    power_range = (-110,13)
            elif "SG384" in response:
                    freq_range = (950*pow(10,3),4.050*pow(10,9))
                    power_range = (-110,13)
            elif "SG386" in response:
                    freq_range = (950*pow(10,3),6.075*pow(10,9))
                    power_range = (-110,13)
            else:
                raise Exception(f"The model of SRS SG380 is not recognized at {self._device_configuration.gpib_address}")
        else:
            if "SG382" in response or "SG384" in response or "SG386" in response:
                # This assumes that the BNC port will be in use 
                freq_range = (0,62.5*pow(10,6))
                power_range = (-47,13)
            else:
                raise Exception(f"The model of SRS SG380 is not recognized at {self._device_configuration.gpib_address}")
        
        # adding relevant parameters to device configuration
        self._device_configuration._srs = _srs
        self._device_configuration._rm = _rm
        self._device_configuration._frequency_range_hz = freq_range
        self._device_configuration._power_range_dbm = power_range

    def close_connection(self):
        # turns off the signal and closes open ports 
        self.turn_off_signal()
        self._device_configuration._srs.close()
        self._device_configuration._rm.close()            


    #########################################################################################################################################################################    
    # Implementation of the abstract signal generator functions 
    #########################################################################################################################################################################    
    @property
    def frequency_range_hz(self):
        """This is meant to take in the frequency range of the device as a tuple in Hz
        """
        return self._device_configuration._frequency_range_hz
    
    @property
    def power_range_dbm(self):
        """This takes in the power range of the device that you are interfacing with as a tuple in dBm
        """
        return self._device_configuration._power_range_dbm

    def set_frequency_hz(self,frequency:int):
        """sets the frequency of the srs 
        """
        self.change_frequency(frequency, unit="Hz")
   
    def get_frequency_hz(self)->float:
        """sets the frequency of the srs 
        """
        return float(self.get_current_frequency())

    def set_power_dbm(self,amplitude:float):
        """Sets the signal power in dBm 
        """
        if self._device_configuration.use_n_type_port:
            self.change_amplitude_n_type(amplitude)
        else:
            self.change_amplitude_bnc(amplitude)
    
    def get_power_dbm(self)->float:
        """Sets the signal power in dBm 
        """
        if self._device_configuration.use_n_type_port:
            return float(self.get_n_type_amplitude())
        else:
            return float(self.get_bnc_amplitude())
        

    def turn_on_signal(self):
        """Turns on the signal source this will map to the specific port in question
          and does not turn on the device just the signal
        """
        if self._device_configuration.use_n_type_port:
            self.n_type_on()
        else:
            self.bnc_on()

    def turn_off_signal(self):
        """This turns off the signal source and will not turn off the device 
        """
        if self._device_configuration.use_n_type_port:
            self.n_type_off()
        else:
            self.bnc_off()

    def load_frequency_list_hz(self,frequency_list):
        """This is meant to be a command to load a frequency list to a device if the device can't do this it can be implemented using the set frequency
            and saving the list as a property to the class triggering you can just iterate through the list 
        """
        self.send_frequency_list(frequency_list)

    def get_frequency_list_hz(self):
        """ Returns a list of the currently loaded frequencies 
        """
        return self.get_frequency_list()

    def iterate_frequency(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        self.trigger_list_item()

    #########################################################################################################################################################################    
    # Cascading commands 
    #########################################################################################################################################################################    
    def get_frequency_list(self):
        size_of_list = int(self.get_list_size())
        frequencies = []

        for i in range(size_of_list):
            freq = self.get_list_point(i)
            frequencies.append(float(self.get_list_point(i).replace(",N,N,N,N,N,N,N,N,N,N,N,N,N,N\r\n","")))

        return frequencies
    
    def send_frequency_list(self,frequency_list):
        # Sends the list of desired frequencies to the SRS through GPIB
        self._device_configuration._srs.query(f"LSTC? {len(frequency_list)}")
        self.clear_status()

        for ind,f in enumerate(frequency_list):
            command = f"LSTP {ind},{f},N,N,N,N,N,N,N,N,N,N,N,N,N,N"
            self._device_configuration._srs.write(command)
        
        self._device_configuration._srs.write("LSTE 1")
    
   
    #########################################################################################################################################################################    
    # Default commands implemented
    #########################################################################################################################################################################    
    def modulation_on(self):
        self._device_configuration._srs.write("MODL 1")
    
    def modulation_off(self):
        self._device_configuration._srs.write("MODL 0")
    
    def modulation_state(self):
        return self._device_configuration._srs.query("MODL?")
    
    def modulation_type(self,type:int):
        """
        0 = AM
        1 = FM
        2 = PhiM (Phase)
        3 = Sweep
        4 = Pulse
        5 = Blank
        6 = IQ
        """

        self._device_configuration._srs.write(f"TYPE {type}")

    def get_modulation_type(self):
        return self._device_configuration._srs.query("TYPE?")
    
    def iq_modulation_noise(self):
        self._device_configuration._srs.write("QFNC 4")
    
    def iq_modulation_external(self):
        self._device_configuration._srs.write("QFNC 5")

    def get_iq_modulation(self):
        return self._device_configuration._srs.query("QFNC?")
    
    def n_type_on(self):
        self._device_configuration._srs.write("ENBR 1")
    
    def n_type_off(self):
        self._device_configuration._srs.write("ENBR 0")
    
    def n_type_state(self):
        return self._device_configuration._srs.query("ENBR?")
    
    def bnc_on(self):
        self._device_configuration._srs.write("ENBL 1")
    
    def bnc_off(self):
        self._device_configuration._srs.write("ENBL 0")
    
    def bnc_state(self):
        return self._device_configuration._srs.query("ENBL?")
    
    def change_frequency(self,frequency,unit= "MHz"):
        if unit == "Hz":
            self._device_configuration._srs.write('FREQ '+str(frequency))
        else:
            self._device_configuration._srs.write(f'FREQ {frequency} {unit}')
    def get_current_frequency(self):
        return self._device_configuration._srs.query("FREQ?")
    
    def change_amplitude_n_type(self,amplitude):
        self._device_configuration._srs.write('AMPR '+str(amplitude))
    
    def get_n_type_amplitude(self):
        return self._device_configuration._srs.query("AMPR?")
    
    def change_amplitude_bnc(self,amplitude):
        self._device_configuration._srs.write('AMPL '+str(amplitude))
    
    def get_bnc_amplitude(self):
        return self._device_configuration._srs.query("AMPL?")
    
    def change_phase(self,phase):
        self._device_configuration._srs.write('PHAS '+str(phase))
    
    def get_phase(self):
        return self._device_configuration._srs.query("PHAS?")
    
    def get_list_point(self,number):
        return self._device_configuration._srs.query(f"LSTP? {number}")

    def get_list_size(self):
        return self._device_configuration._srs.query("LSTS?")

    def trigger_list_item(self):
        # Triggers the next item on the list for the SRS using the DAQ
        self._device_configuration._srs.write("*TRG")
    

    def clear_status(self):
        return self._device_configuration._srs.write("*CLS")
    
    def check_connection(self):
        response =  self._device_configuration._srs.query("*IDN?")
        if "Stanford Research Systems,SG384" in response:
            return response
        else:
            raise Exception("Failed to confirm srs connection id may be incorrect")
        

