__all__ = ["SG380Channels","SG380"]

# importing third party modules 
import pyvisa
from enum import IntEnum
import numpy.typing as npt
import numpy as np

# Importing abstract classes 
from NV_ABJ.abstract_interfaces.microwave_source import MicrowaveSource
class SG380Channels(IntEnum):
    n_type:int = 0
    bnc:int = 1


class SG380(MicrowaveSource):
    """This is where the constraints for connecting to the correct signal generator are stored such as the address and if we want to use the n_type_port

    Args:
        gpib_address: str = The address that you connect to the srs with
        channel: SG380Channels  =  You can choose either n_type (int 0) or bnc (int 1)
    """

    def __init__(self,gpib_address: str,channel: SG380Channels = SG380Channels.n_type):
        self.gpib_address = gpib_address
        self.channel = channel
        
        # These are made by the make connection class
        self._frequency_range_hz: tuple = None
        self._power_range_dbm:tuple = None
        self._rm = None
        self._srs = None

    def make_connection(self):
        
        # Takes a daq card id, daq channel, and a gpib id and returns a class to control the srs
        _rm = pyvisa.ResourceManager()
        _srs = _rm.open_resource(self.gpib_address)

        # Clear status
        _srs.write("*CLS")

        # Check model number from ID 
        response = str(_srs.query("*IDN?"))

        if self.channel:
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
                raise Exception(f"The model of SRS SG380 is not recognized at {self.gpib_address}")
        else:
            if "SG382" in response or "SG384" in response or "SG386" in response:
                # This assumes that the BNC port will be in use 
                freq_range = (0,62.5*pow(10,6))
                power_range = (-47,13)
            else:
                raise Exception(f"The model of SRS SG380 is not recognized at {self.gpib_address}")
        
        # adding relevant parameters to device configuration
        self._srs = _srs
        self._rm = _rm
        self._frequency_range_hz = freq_range
        self._power_range_dbm = power_range

    def close_connection(self):
        # turns off the signal and closes open ports 
        self.turn_off_signal()
        self._srs.close()
        self._rm.close()            


    #########################################################################################################################################################################    
    # Abstract MicrowaveSource Functions 
    #########################################################################################################################################################################    
    @property
    def frequency_range_hz(self):
        """This is meant to take in the frequency range of the device as a tuple in Hz
        """
        return self._frequency_range_hz
    
    @property
    def amplitude_range_dbm(self):
        """This takes in the power range of the device that you are interfacing with as a tuple in dBm
        """
        return self._power_range_dbm

    def prime_sinusoidal_rf(self,frequency_list_hz:npt.NDArray[np.float64],
                        rf_amplitude_dbm:npt.NDArray[np.float64],
                        *args,**kwargs):
        """Loads a frequency list into the sg380. This will immediately turn on the sg380 and it is assumed that that the duration will 
        be controlled by a microwave switch

         Args:
            frequency_list_hz (npt.NDArray[np.float64]): A floating point numpy array that consists of the frequency in Hz 
            rf_amplitude_dbm (npt.NDArray[np.float64]): A floating point numpy array of the amplitude of the un-modulated sine wave dBm
        """

        # Setting the SRS frequency 
        match self.channel:
            case SG380Channels.n_type:
                self.send_list(frequency_list_hz=frequency_list_hz,
                                amplitude_list_n_type_dbm=rf_amplitude_dbm)
            case SG380Channels.bnc:
                self.send_list(frequency_list_hz=frequency_list_hz,
                                amplitude_list_bnc_dbm=rf_amplitude_dbm)

        # Turning on the signal 
        self.turn_on_signal()
    
    def turn_on_signal(self):
        """Turns on the signal source this will map to the specific port in question
          and does not turn on the device just the signal
        """
        match self.channel:
            case SG380Channels.n_type:
               self.n_type_on()
            case SG380Channels.bnc:
                self.bnc_on()


    def turn_off_signal(self):
        """This turns off the signal source and will not turn off the device 
        """
        match self.channel:
            case SG380Channels.n_type:
               self.n_type_off()
            case SG380Channels.bnc:
                self.bnc_off()


    def iterate_next_waveform(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        self.trigger_list_item() # Triggers next in list

    #########################################################################################################################################################################    
    # SG380 Commands 
    #########################################################################################################################################################################    
    def set_power_dbm(self,amplitude:float):
        """Sets the signal power in dBm 
        """
        match self.channel:
            case SG380Channels.n_type:
                self.change_amplitude_n_type(amplitude)
            case SG380Channels.bnc:
                self.change_amplitude_bnc(amplitude)
    
    def get_power_dbm(self)->float:
        """Sets the signal power in dBm 
        """
        match self.channel:
            case SG380Channels.n_type:
                return float(self.get_n_type_amplitude())
            case SG380Channels.bnc:
                return float(self.get_bnc_amplitude())


    def get_list(self):
        """returns the list items 

        Returns:
            _type_: _description_
        """
        size_of_list = int(self.get_list_size())
        sg380_list = []

        for i in range(size_of_list):
            sg380_list.append(self.get_list_point(i).replace("\r\n","").split(","))
        return sg380_list
    
    def send_list(self,frequency_list_hz:npt.NDArray[np.float64]=[],
                  phase_deg:npt.NDArray[np.float64]=[],
                   amplitude_list_bnc_dbm:npt.NDArray[np.float64]=[],
                   offset_for_bnc:npt.NDArray[np.float64]=[],
                   amplitude_list_n_type_dbm:npt.NDArray[np.float64]=[],
                   front_panel_display_list:npt.NDArray[np.float64]=[],
                   enable_disable_list:npt.NDArray[np.int8]=[],
                   modulation_type_list:npt.NDArray=[],
                   modulation_function_list:npt.NDArray=[],
                   modulation_rate_list:npt.NDArray=[],
                   modulation_deviation_list:npt.NDArray=[],
                   amplitude_of_clock_list:npt.NDArray=[],
                   offset_of_clock_output:npt.NDArray=[],
                   amplitude_of_hf_list:npt.NDArray=[],
                   offset_from_rear_dc_list:npt.NDArray=[]):
        
        """ Settings for the list and how the command structure from the manual SG380

            1 Frequency FREQ
            2 Phase PHAS
            3 Amplitude of LF (BNC output) AMPL
            4 Offset of LF (BNC output) OFSL
            5 Amplitude of RF (Type-N output) AMPR
            6 Front panel display DISP
            7 Enables/Disables
                    Bit 0: Enable modulation MODL
                    Bit 1: Disable LF (BNC output) ENBL
                    Bit 2: Disable RF (Type-N output) ENBR
                    Bit 3: Disable Clock output ENBC
                    Bit 4: Disable HF (RF doubler output) ENBH
            8 Modulation type TYPE
            9 Modulation function
                    AM/FM/ ΦM MFNC
                    Sweep SFNC
                    Pulse/Blank PFNC
                    IQ QFNC
            10 Modulation rate
                    AM/FM/ΦM modulation rate RATE
                    Sweep rate SRAT
                    Pulse/Blank period PPER, RPER
            11 Modulation deviation
                    AM ADEP, ANDP
                    FM FDEV, FNDV
                    ΦM PDEV, PNDV
                    Sweep SDEV
                    Pulse/Blank PWID
            12 Amplitude of clock output AMPC
            13 Offset of clock output OFSC
            14 Amplitude of HF (RF doubler output) AMPH
            15 Offset of rear DC OFSD
        """
        # Finding max list 
        all_command_lists = [list(frequency_list_hz),
                            list(phase_deg),
                            list(amplitude_list_bnc_dbm),
                            list(offset_for_bnc),
                            list(amplitude_list_n_type_dbm),
                            list(front_panel_display_list),
                            list(enable_disable_list),
                            list(modulation_type_list),
                            list(modulation_function_list),
                            list(modulation_rate_list),
                            list(modulation_deviation_list),
                            list(amplitude_of_clock_list),
                            list(offset_of_clock_output),
                            list(amplitude_of_hf_list),
                            list(offset_from_rear_dc_list)]
        
        max_list_length = max([len(i) for i in all_command_lists])

        # Making all lists the same length 
        for lst in all_command_lists:
            for i in range(max_list_length-len(lst)):
                lst.append("N")
              
        self.clear_status()

        # Creating the list
        self._srs.query(f"LSTC? {max_list_length}")

        count = 0
        for f,p,amp_b,off_b,amp_n_type,front_disp,ena_dis,mod_type,mod_func,mod_rate,mod_dev,amp_clock,off_clock,amp_hf,off_rear in zip(*all_command_lists):
            command = "LSTP {},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(count,f,p,amp_b,off_b,amp_n_type,front_disp,ena_dis,mod_type,mod_func,mod_rate,mod_dev,amp_clock,off_clock,amp_hf,off_rear)
            count = count + 1
            self._srs.write(command)
        
        self._srs.write(f"LSTE 1")
    
   
    #########################################################################################################################################################################    
    # Default commands implemented
    #########################################################################################################################################################################    
    def modulation_on(self):
        self._srs.write("MODL 1")
    
    def modulation_off(self):
        self._srs.write("MODL 0")
    
    def modulation_state(self):
        return self._srs.query("MODL?")
    
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

        self._srs.write(f"TYPE {type}")

    def get_modulation_type(self):
        return self._srs.query("TYPE?")
    
    def iq_modulation_noise(self):
        self._srs.write("QFNC 4")
    
    def iq_modulation_external(self):
        self._srs.write("QFNC 5")

    def get_iq_modulation(self):
        return self._srs.query("QFNC?")
    
    def n_type_on(self):
        self._srs.write("ENBR 1")
    
    def n_type_off(self):
        self._srs.write("ENBR 0")
    
    def n_type_state(self):
        return self._srs.query("ENBR?")
    
    def bnc_on(self):
        self._srs.write("ENBL 1")
    
    def bnc_off(self):
        self._srs.write("ENBL 0")
    
    def bnc_state(self):
        return self._srs.query("ENBL?")
    
    def change_frequency(self,frequency,unit= "MHz"):
        if unit == "Hz":
            self._srs.write('FREQ '+str(frequency))
        else:
            self._srs.write(f'FREQ {frequency} {unit}')
    def get_current_frequency(self):
        return self._srs.query("FREQ?")
    
    def change_amplitude_n_type(self,amplitude):
        self._srs.write('AMPR '+str(amplitude))
    
    def get_n_type_amplitude(self):
        return self._srs.query("AMPR?")
    
    def change_amplitude_bnc(self,amplitude):
        self._srs.write('AMPL '+str(amplitude))
    
    def get_bnc_amplitude(self):
        return self._srs.query("AMPL?")
    
    def change_phase(self,phase):
        self._srs.write('PHAS '+str(phase))
    
    def get_phase(self):
        return self._srs.query("PHAS?")
    
    def get_list_point(self,number):
        return self._srs.query(f"LSTP? {number}")

    def get_list_size(self):
        return self._srs.query("LSTS?")

    def trigger_list_item(self):
        # Triggers the next item on the list for the SRS using the DAQ
        self._srs.write("*TRG")
    
    def wait_for_command_execution(self)->None:
        """The instrument will not process further commands until all prior commands
        including this one have completed. 
        """
        self._srs.write("*WAI")
    

    def clear_status(self):
        return self._srs.write("*CLS")
    
    def check_connection(self):
        response =  self._srs.query("*IDN?")
        if "Stanford Research Systems,SG384" in response:
            return response
        else:
            raise Exception("Failed to confirm srs connection id may be incorrect")
