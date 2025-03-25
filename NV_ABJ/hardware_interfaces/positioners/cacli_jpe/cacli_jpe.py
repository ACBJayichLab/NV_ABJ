"""
This is a class that is based on interactions with the provided Cacli.exe file from JPE in order to use this you must add the location of the Cacli.exe
folder to the system environment variables for example if you saved it to "C:" you would add "C:" to the system variables path
"""
import subprocess
from dataclasses import dataclass

from NV_ABJ import PositionerSingleAxis

@dataclass
class ConfigurationCacliJpe:
    piezo_driver_target:str 
    piezo_address:int
    piezo_stage:str
    temperature_kelvin:int
    frequency_hz:int
    relative_step_size_percent:float
    tqfr_percent:float


class CacliJpe(PositionerSingleAxis):

    def __init__(self,device_configuration:ConfigurationCacliJpe):
        self._device_configuration_class = device_configuration
        
    #########################################################################################################################################################################    
    # Implementation of the abstract signal generator functions 
    #########################################################################################################################################################################    
    @property
    def device_configuration_class(self):
        return self._device_configuration_class
    
    def move_positioner(self,direction,steps):
        """
        The move command starts moving an actuator with specified parameters. If an RSM or OEM2 is
        installed, the actuator position will be tracked automatically if the actuator is fitted with a Resistive
        Linear Sensor (-RLS option) or Cryo Optical Encoder (-COE option) and connected to one of the channels
        of the RSM or OEM2 module.

        Command [foll. by enter] cacli MOV [ADDR] [STAGE] [TEMP] [DIR] [FREQ] [REL] [STEPS] [TRQFR]
        Command (example) cacli MOV 1 1 600 100 0 293 CLA2601 1
        
        cacli @1038E201905-14 MOV 3 CLA2601 300 0 200 75 100 1.0

        Response (example) Actuating the stage.
        """
        piezo_driver_target = self._device_configuration_class.piezo_driver_target
        piezo_address = self._device_configuration_class.piezo_address
        piezo_stage = self._device_configuration_class.piezo_stage
        temperature_kelvin = self._device_configuration_class.temperature_kelvin
        frequency_hz = self._device_configuration_class.frequency_hz
        relative_step_size = self._device_configuration_class.relative_step_size_percent
        trqfr = self._device_configuration_class.tqfr_percent

        command = f"cacli @{piezo_driver_target} MOV {piezo_address} {piezo_stage} {temperature_kelvin} {direction} {frequency_hz} {relative_step_size} {steps} {trqfr}"
        response = subprocess.call(command)

        return response

    def stop_positioner(self,normal_output=True):
        """
        Emergency stop all piezos in motion
        """
        piezo_driver_target = self._device_configuration_class.piezo_driver_target
        piezo_address = self._device_configuration_class.piezo_address

        command = f"cacli @{piezo_driver_target} STP {piezo_address}"

        if normal_output:
            response = subprocess.call(command)
            return response
        else:
            #This is to mute the response for use with the GUI
            subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            return None

        
    # For a connected device there isn't much to check with a third party controlled device 
    def make_connection(self):
        if not self.check_cacli_connection():
            raise Exception("Failed to connect to device")
    def close_connection(self):
        pass
    

    #########################################################################################################################################################################    
    # Cascading commands 
    #########################################################################################################################################################################    
    def check_cacli_connection(self):
        
        # call command
        command =  ["cacli","/USB"]
        response = subprocess.check_output(command)
        
        # split responses by new lines because that is hoqw cacli formats 
        responses = str(response).replace("\\r","").replace("\\t","").replace("'","").split("\\n")

        #find which controller ids are attached 
        ids = []
        
        for r in responses:
            if ") CryoActuator Control System (" in r:
                ids.append(r.split(") CryoActuator Control System (")[1].replace(")",""))

        # check if controller id is connected 
        if self.piezo_driver_target in ids:
            target_connected = True
        else:
            target_connected = False
            
        return ids, target_connected

    def set_frequency_hz(self, frequency_hz):
        self._device_configuration_class.frequency_hz(frequency_hz)
    
    def set_relative_step_size(self, relative_step_size):
        self._device_configuration_class.relative_step_size_percent(relative_step_size)
    
    def set_temperature_kelvin(self, temperature_kelvin):
        self._device_configuration_class.temperature_kelvin(temperature_kelvin)
    
    def set_tqfr(self, tqfr):
        self._device_configuration_class.tqfr_percent(tqfr)

    def __repr__(self):
        return f"Target Id: {self.piezo_driver_target}\nAddress: {self.piezo_address}\nStage: {self.piezo_stage}"

