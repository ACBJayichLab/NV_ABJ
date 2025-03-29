_all_ = ["CacliJpeConfig","CacliJpe","CacliVersion"]
"""
This is a class that is based on interactions with the provided Cacli.exe file from JPE in order to use this you must add the location of the Cacli.exe
folder to the system environment variables for example if you saved it to "C:" you would add "C:" to the system variables path

This is also only programmed for use with USB at the moment. My LAN connection has never worked unfortunately so I could not program it for general cases
"""
from subprocess import Popen, PIPE
import time
from dataclasses import dataclass
from enum import IntEnum

from NV_ABJ import PositionerSingleAxis

class CacliVersion(IntEnum):
    """These are the different versions of Calci that are used so far and they have slightly different command structures 
    https://www.jpe-innovations.com/cryo-uhv-products/cryo-positioning-systems-controller/ 
    find the appropriate version on JPEs website and save the manual and software into the Cacli versions folder 
    """
    v4 = 4 # 1038E201410-004, 1038E201406-XXX
    v6 = 6 # 1038E201905-XX, 1038E201910-XX, 1039E201911-XX
    v7 = 7 # Firmware not on the list (newer models)

@dataclass
class CacliJpeConfig:
    piezo_driver_target:str 
    piezo_address:int
    piezo_stage:str
    temperature_kelvin:int
    frequency_hz:int
    relative_step_size_percent:float
    torque_factor:int
    cacli_version:CacliVersion = CacliVersion.v7 # There are slight differences between different commands 
    time_out:float = 0.1
    delay_between_attempts_s:int = 5
    number_of_attempts:int = 5

class CacliJpe(PositionerSingleAxis):

    def __init__(self,device_configuration:CacliJpeConfig):
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
        trqfr = self._device_configuration_class.torque_factor
        version = self._device_configuration_class.cacli_version

        match version:
            case CacliVersion.v6:
                command = f"cacli @{piezo_driver_target} MOV {piezo_address} {piezo_stage} {temperature_kelvin} {direction} {frequency_hz} {relative_step_size} {steps} {trqfr}"
            case CacliVersion.v7:
                command = f"cacli @{piezo_driver_target} MOV {piezo_address} {direction} {frequency_hz} {relative_step_size} {steps} {temperature_kelvin} {piezo_stage} {trqfr}"
            case _:
                raise NotImplemented(f"The cacli version {version.name} has not been implemented yet")
        
        response = self.try_command(command)

        return response

    def stop_positioner(self,normal_output=True):
        """
        Emergency stop all piezos in motion
        """
        piezo_driver_target = self._device_configuration_class.piezo_driver_target
        piezo_address = self._device_configuration_class.piezo_address

        command = f"cacli @{piezo_driver_target} STP {piezo_address}"

        if normal_output:

            response = self.try_command(command)
            return response
        else:
            #This is to mute the response for use with the GUI
            self.try_command(command)
            return None

        
    # For a connected device there isn't much to check with a third party controlled device 
    def make_connection(self):
        if not self.check_cacli_connection():
            raise Exception("Failed to connect to specified device")
        
    def close_connection(self):
        pass
    

    #########################################################################################################################################################################    
    # Base Commands 
    #########################################################################################################################################################################    
    def try_command(self,command,retry_after_failure=False):
        number_attempts = self._device_configuration_class.number_of_attempts
        for n in range(number_attempts):
            try:
                p = Popen(command.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output, err = p.communicate(b"input data that is passed to subprocess' stdin",timeout=self._device_configuration_class.time_out)
                return output.decode("utf-8")
            except:
                if retry_after_failure:
                    time.sleep(self._device_configuration_class.delay_between_attempts_s)
                else:
                    # There is a error with certain commands like MOV for newer CLI programs by JPE that means the command line may not receive an exit to new line 
                    # This means that it will never time out because it maintains a open line so if we want to continue this must be timed out 
                    # This is unfortunately not something we are likely able to fix 
                    return -1
                
        raise Exception(f"Failed to execute {command} after {number_attempts} attempts")
        
    def check_cacli_connection(self):
        
        # call command
        command =  "cacli /USB"

        response = self.try_command(command, retry_after_failure=True)
        
        # check if controller id is connected 
        if self._device_configuration_class.piezo_driver_target in response:
            target_connected = True
        else:
            target_connected = False
            
        return target_connected


    def set_frequency_hz(self, frequency_hz):
        self._device_configuration_class.frequency_hz = frequency_hz
    
    def set_relative_step_size(self, relative_step_size):
        self._device_configuration_class.relative_step_size_percent = relative_step_size
    
    def set_temperature_kelvin(self, temperature_kelvin):
        self._device_configuration_class.temperature_kelvin = temperature_kelvin
    
    def set_tqfr(self, tqfr):
        self._device_configuration_class.torque_factor = tqfr

    def __repr__(self):
        return f"Target Id: {self.piezo_driver_target}\nAddress: {self.piezo_address}\nStage: {self.piezo_stage}"


if __name__ == "__main__":
    target_id = '1038E201905-12'

    cfg_x = CacliJpeConfig(piezo_driver_target=target_id,
                         piezo_address=4,
                         piezo_stage="CS021-RLS.X",
                         temperature_kelvin=300,
                         frequency_hz=250,
                         relative_step_size_percent=100,
                         torque_factor=1)
    
    cfg_y = CacliJpeConfig(piezo_driver_target=target_id,
                         piezo_address=5,
                         piezo_stage="CS021-RLS.Y",
                         temperature_kelvin=300,
                         frequency_hz=250,
                         relative_step_size_percent=100,
                         torque_factor=1)
    
    cfg_z = CacliJpeConfig(piezo_driver_target=target_id,
                         piezo_address=6,
                         piezo_stage="CS021-RLS.Z",
                         temperature_kelvin=300,
                         frequency_hz=250,
                         relative_step_size_percent=100,
                         torque_factor=1)
    
    with CacliJpe(cfg_y) as jpe:
        
        # print(jpe.check_cacli_connection())
        jpe.move_positioner(1,10)
        # jpe.stop_positioner()