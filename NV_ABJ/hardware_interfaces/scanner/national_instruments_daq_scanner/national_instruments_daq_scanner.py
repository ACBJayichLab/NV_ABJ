"""
This is a national instruments controlling class that also inclues class that are directly controlled by the DAQ
These instruments include the SRS becuase it is triggered by the DAQ when a list is itterated,
the NpPoint Z confocal piezo becuase the daq provides a voltage that it chases to set the z height,
the attocube piezos becuase they relly on an input and ouput of the daq to be monitored and controlled ,
the fast steering mirror because it is controlled in xy position by the daq, and the photodiode that collects the green power 
"""
import numpy as np # used to calculate means and normal error 
import time # used for timing out the daq interactions
from dataclasses import dataclass

# National instruments imports 
import nidaqmx

from NV_ABJ import ScannerSingleAxis

@dataclass
class NationalInstrumentsDaqSingleAxisScannerConfiguration:
    """
    conversion_volts_per_meter:float = How many volts would it be to move the scanner one meter yes this is large but thats just for conversion to standard units 

    device_name_output:str = Device name for the output e.g. "PXI1Slot3"
    channel_name_output:str = Name for the channel output e.g. "ao0"
    device_name_input:str = Device name that the voltage input is attached to e.g. "PXI1Slot3" default None
    channel_name_input:str = Name for the channel input e.g. "ai0" default None

    If you want to set limits to protect the scanner 
    position_limits_m:tuple = (Lower limit on distance, Upper limit on distance) in meters. This is to stop over-volting or going past a arbitrary limit. default (None,None) 

    This is the settings for how the daq will wait for a voltage to be reached 
    timeout_waiting_for_voltage_set_s:int = 10
    stability_voltage_difference:float = 0.004
    voltage_sample_rate:int=1000
    samples_per_read:int=100
    
    """
    conversion_volts_per_meter_setting:float

    device_name_output:str
    channel_name_output:str
    device_name_input:str = None
    channel_name_input:str = None

    # Limits on the device if we want to set them
    position_limits_m:tuple = (None,None) # This is based on the scanner if it has a limit of 3um or a voltage limit it will throw an error if it is exceeded 
    conversion_volts_per_meter_getting:float = None # If the reading voltage is different to the setting voltage conversion (set to None results in the conversions being equal)

    #This is the configuration for the stabilization of the scanner 
    timeout_waiting_for_voltage_set_s:int = 10
    stability_voltage_difference:float = 0.004
    voltage_sample_rate:int=1000
    samples_per_read:int=100

    _position_m:float = None # Where the device is set to for tracking purposes only




class NationalInstrumentsDaqSingleAxisScanner(ScannerSingleAxis):

    def __init__(self,device_configuration:NationalInstrumentsDaqSingleAxisScannerConfiguration):
        self._device_configuration = device_configuration

    #########################################################################################################################################################################    
    # Implementation of the abstract single axis scanner class
    #########################################################################################################################################################################    
    def set_position_m(self, position):
        voltage = self.position_to_voltage(position)

        # Checks to see if the scanner controlled by the daq is monitored by a port or not (attocube positioner versus fsm functionality)
        if self._device_configuration.channel_name_input != None:
            self.wait_for_voltage(voltage)
        else:
            self.voltage_out(voltage)
            self._device_configuration._position_m = position
        
    def get_position_m(self):
        if self._device_configuration.channel_name_input != None:
            voltage = self.read_voltage()
            if self._device_configuration.conversion_volts_per_meter_getting == None:
                return voltage/self._device_configuration.conversion_volts_per_meter_setting
            else:
                return voltage/self._device_configuration.conversion_volts_per_meter_getting 

        else:
            return self._device_configuration._position_m
    
    # This is handled by the daq
    def make_connection(self):
        pass
    
    def close_connection(self):
        pass
    
    @property
    def device_configuration_class(self):
        return self._device_configuration
    
    #########################################################################################################################################################################    
    # Implementation of basic daq functions
    #########################################################################################################################################################################    
    def position_to_voltage(self,position):

        # Getting the limits from the configuration to check
        position_limits_m = self._device_configuration.position_limits_m

        # Checks for position 
        if position_limits_m[0] != None:
            if position_limits_m[0] > position:
                raise ValueError(f"Can not enter a value smaller than lower position limit of {position_limits_m[0]}")
        if position_limits_m[1] != None:
            if position_limits_m[1] < position:
                raise ValueError(f"Can not enter a value larger than upper position limit of {position_limits_m[1]}")
        
        # This will set the voltage if no errors are returned 
        voltage_set = self._device_configuration.conversion_volts_per_meter_setting*position
        
        return voltage_set

    def voltage_out(self,voltage):
        channel_address_out = self._device_configuration.device_name_output+"/"+self._device_configuration.channel_name_output
        try:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(channel_address_out)
                task.write(voltage)

        except nidaqmx.DaqError as e:
            raise Exception(f"DAQmx error occurred and could not set voltage: {e}")

    
    def read_voltage(self):
        channel_address_in = self._device_configuration.device_name_input+"/"+self._device_configuration.channel_name_input

        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(channel_address_in)
                voltage = task.read()        

        except nidaqmx.DaqError as e:
            raise Exception(f"DAQmx error occurred: {e}")
        
        else:
            return voltage

    
    def wait_for_voltage(self,voltage):
        channel_address_in = self._device_configuration.device_name_input+"/"+self._device_configuration.channel_name_input

        try:
            self.voltage_out(voltage)
            timeout_start = time.time()

            # This doesn't actually use the getting value to determine distance it simply waits for the voltage to settle 

            try:

                with nidaqmx.Task() as task:
                    task.ai_channels.add_ai_voltage_chan(channel_address_in, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
                    task.timing.cfg_samp_clk_timing(rate=self._device_configuration.voltage_sample_rate,
                                                     sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=self._device_configuration.samples_per_read)

                    task.start()
                    
                    # getting the data until its deviation is lower than desired or timed out
                    while time.time() < timeout_start + self._device_configuration.timeout_waiting_for_voltage_set_s:
                        # aquiring data
                        data = task.read(number_of_samples_per_channel=self._device_configuration.samples_per_read)
                        
                        # getting the deviation of the data
                        deviation = np.std(data)
                        if deviation <= self._device_configuration.stability_voltage_difference:
                            #exiting while loop when the voltage deviation is lower or equal to the desired 
                            return np.mean(data),deviation
                    print("Voltage timed out. Could not reach requested voltage for the daq output")



            except nidaqmx.DaqError as e:
                raise Exception(f"DAQmx error occurred: {e}")
               
        except:
            raise Exception("Failed to stabilize voltage output")
    
