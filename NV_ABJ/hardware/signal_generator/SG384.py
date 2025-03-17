# importing the interface module 
from NV_ABJ.interface.signal_generator_interface import SignalGeneratorInterface

# importing third party modules 
import pyvisa

class SG384(SignalGenerator):
    """This is a implementation for the SG384 for the base qudi application with the signal generator code 
    """

    def __init__(self,gpib_identification:str,gpib_class,frequency_hz_range:tuple,power_dbm_range:tuple,n_type_port:bool=True):
        """

        Args:
            gpib_identification (str): This is the pyvisa identification of the port that the srs is located at 
            gpib_class (pyvisa class): this is done so we can create a singular class and not spend resources remaking it every call
            frequency_hz_range (tuple): (low frequency, high frequency)
            power_dbm_range (tuple): (low power, high power)
            port (bool, optional): This is what controls the port that is use for the SRS can be N-type or BNC. Defaults to True for N-Type.
        """
        self.gpib_identification = gpib_identification
        self.gpib_class = gpib_class
        self._frequency_hz_range = frequency_hz_range # this is set this way to be an immutable object 
        self._power_dbm_range = power_dbm_range
        self.n_type_port = n_type_port

    # Class methods for making new instances 
    @classmethod
    def make_gpib_connection(cls,gpib_identification:str,frequency_hz_range_low:float,frequency_hz_range_high:float,power_dbm_low:float,power_dbm_high:float):
        
        # Getting device constraints 
        freq_range = (frequency_hz_range_low,frequency_hz_range_high)
        power_range = (power_dbm_low,power_dbm_high)

        # Takes a daq card id, daq channel, and a gpib id and returns a class to control the srs
        srs = pyvisa.ResourceManager().open_resource(gpib_identification)
        return cls(gpib_identification,srs,freq_range,power_range)


    #########################################################################################################################################################################    
    # Implementation of the abstract signal generator functions 
    #########################################################################################################################################################################    
    def on_activate(self):
        """ Initialization performed during activation of the module.
        """
        pass

    def on_deactivate(self):
        """ Cleanup performed during deactivation of the module.
        """
        pass

    @property
    def frequency_range_hz(self):
        """This is meant to take in the frequency range of the device as a tuple in Hz
        """
        return self._frequency_hz_range
    
    @property
    def power_range_dbm(self):
        """This takes in the power range of the device that you are interfacing with as a tuple in dBm
        """
        return self._power_dbm_range

    def set_frequency_hz(self,frequency):
        """sets the frequency of the srs 
        """
        self.change_frequency(frequency)


    def set_power_dbm(self,amplitude):
        """Sets the signal power in dBm 
        """
        if self.n_type_port:
            self.change_amplitude_n_type(amplitude)
        else:
            self.change_amplitude_bnc(amplitude)

    def turn_on_signal(self):
        """Turns on the signal source this will map to the specific port in question
          and does not turn on the device just the signal
        """
        if self.n_type_port:
            self.n_type_on()
        else:
            self.bnc_on()

    def turn_off_signal(self):
        """This turns off the signal source and will not turn off the device 
        """
        if self.n_type_port:
            self.n_type_off()
        else:
            self.bnc_off()

    def load_frequency_list_hz(self,frequency_list):
        """This is meant to be a command to load a frequency list to a device if the device can't do this it can be implemented using the set frequency
            and saving the list as a property to the class triggering you can just iterate through the list 
        """
        self.send_frequency_list(frequency_list)

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
        self.gpib_class.query(f"LSTC? {len(frequency_list)}")
        self.clear_status()

        for ind,f in enumerate(frequency_list):
            command = f"LSTP {ind},{f},N,N,N,N,N,N,N,N,N,N,N,N,N,N"
            self.gpib_class.write(command)
        
        self.gpib_class.write("LSTE 1")
    
   
    #########################################################################################################################################################################    
    # Default commands implemented
    #########################################################################################################################################################################    
    def modulation_on(self):
        self.gpib_class.write("MODL 1")
    
    def modulation_off(self):
        self.gpib_class.write("MODL 0")
    
    def modulation_state(self):
        return self.gpib_class.query("MODL?")
    
    def modulation_type(self,tpye:int):
        """
        0 = AM
        1 = FM
        2 = PhiM (Phase)
        3 = Sweep
        4 = Pulse
        5 = Blank
        6 = IQ
        """

        self.gpib_class.write(f"TYPE {type}")

    def get_modulation_type(self):
        return self.gpib_class.query("TYPE?")
    
    def iq_modulation_noise(self):
        self.gpib_class.write("QFNC 4")
    
    def iq_modulation_external(self):
        self.gpib_class.write("QFNC 5")

    def get_iq_modulation(self):
        return self.gpib_class.query("QFNC?")
    
    def n_type_on(self):
        self.gpib_class.write("ENBR 1")
    
    def n_type_off(self):
        self.gpib_class.write("ENBR 0")
    
    def n_type_state(self):
        return self.gpib_class.query("ENBR?")
    
    def bnc_on(self):
        self.gpib_class.write("ENBL 1")
    
    def bnc_off(self):
        self.gpib_class.write("ENBL 0")
    
    def bnc_state(self):
        return self.gpib_class.query("ENBL?")
    
    def change_frequency(self,frequency,unit= "MHz"):
        self.gpib_class.write('FREQ '+str(frequency)+' MHz')
    
    def get_frequency(self):
        return self.gpib_class.query("FREQ?")
    
    def change_amplitude_n_type(self,amplitude):
        self.gpib_class.write('AMPR '+str(amplitude))
    
    def get_n_type_amplitude(self):
        return self.gpib_class.query("AMPR?")
    
    def change_amplitude_bnc(self,amplitude):
        self.gpib_class.write('AMPL '+str(amplitude))
    
    def get_bnc_amplitude(self):
        return self.gpib_class.query("AMPL?")
    
    def change_phase(self,phase):
        self.gpib_class.write('PHAS '+str(phase))
    
    def get_phase(self):
        return self.gpib_class.query("PHAS?")
    
    def get_list_point(self,number):
        return self.gpib_class.query(f"LSTP? {number}")

    def get_list_size(self):
        return self.gpib_class.query("LSTS?")

    def trigger_list_item(self):
        # Triggers the next item on the list for the SRS using the DAQ
        self.gpib_class.write("*TRG")
    

    def clear_status(self):
        return self.gpib_class.write("*CLS")
    
    def check_connection(self):
        response =  self.gpib_class.query("*IDN?")
        if "Stanford Research Systems,SG384" in response:
            return response
        else:
            raise Exception("Failed to confirm srs connection id may be incorrect")
        
    

if __name__ == "__main__":

    # Listing all available ports
    rm = pyvisa.ResourceManager()
    list_data = rm.list_resources()
    print(list_data)

    
    srs_info = "GPIB0::27::INSTR"
    frequency_hz_range_low = 950*pow(10,3)
    frequency_hz_range_high = 4.050*pow(10,9)
    power_dbm_low = -110
    power_dbm_high = 16.5
    

    Srs = SG384.make_gpib_connection(srs_info,frequency_hz_range_low,frequency_hz_range_high,power_dbm_low,power_dbm_high)
    # Srs.check_connection()
    # Srs.change_frequency(3500)
    # print(Srs.get_frequency())
    # Srs.change_amplitude_n_type(-100)
    # print(Srs.get_amplitude())
    # Srs.change_phase(10)
    # print(Srs.get_phase())

    # Srs.rf_on()
    # print(Srs.rf_state())

    # Srs.rf_off()
    # print(Srs.rf_state())
    
