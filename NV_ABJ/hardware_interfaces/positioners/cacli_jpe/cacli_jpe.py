__all__ = ["CacliJpeCadm2","CacliVersion"]
"""
This is a class that is based on interactions with the provided Cacli.exe file from JPE in order to use this you must add the location of the Cacli.exe
folder to the system environment variables for example if you saved it to "C:" you would add "C:" to the system variables path

This is also only programmed for use with USB at the moment. My LAN connection has never worked unfortunately so I could not program it for general cases
"""
from subprocess import Popen, PIPE
import time
from enum import IntEnum

# importing abstract class
from NV_ABJ.abstract_interfaces.positioner import PositionerSingleAxis

class CacliVersion(IntEnum):
    """These are the different versions of Calci that are used so far and they have slightly different command structures 
    https://www.jpe-innovations.com/cryo-uhv-products/cryo-positioning-systems-controller/ 
    find the appropriate version on JPEs website and save the manual and software into the Cacli versions folder 
    """
    v4 = 4 # 1038E201410-004, 1038E201406-XXX
    v6 = 6 # 1038E201905-XX, 1038E201910-XX, 1039E201911-XX
    v7 = 7 # Firmware not on the list (newer models)

class CacliJpeCadm2(PositionerSingleAxis):

    def __init__(self,piezo_driver_target:str,piezo_address:int,piezo_stage:str,temperature_kelvin:float,
                frequency_hz:int,relative_step_size_percent:float,
                torque_factor:int = 1,cacli_version:CacliVersion = CacliVersion.v7,
                time_out:float = 0.1,delay_between_attempts_s:int = 5,number_of_attempts:int = 5):
        """This is a basic command method for controlling the JPE positioners over USB using the cacli commands 
            This treats the JPE as a PositionerSingleAxis class it is for controlling a CADM2 module by JPE

        Args:
            piezo_driver_target (str): The address of the communication box e.g. 1038E201410-004
            piezo_address (int): A value between 1 and 6 for where the piezo driver is located in the target device 
            piezo_stage (str): The type of stage that you are driving e.g. "CS021.Z" you can find available stages with cacli /STAGES match with your type
            temperature_kelvin (float): Temperature in kelvin of the JPE
            frequency_hz (int): What frequency the JPE is driven at 
            relative_step_size_percent (float): This is the relative step 0 to 100% you can reduce vibrations by reducing step size
            torque_factor (int, optional): For a knob how strongly it is driven. Defaults to 1.
            cacli_version (CacliVersion, optional): The version of cacli installed on the computer. Defaults to CacliVersion.v7.
            jpe_module (JpeModule, optional): Select the type of module you are running your JPE on 
            time_out (float, optional): Some versions don't exit on a move or cause errors this times out of the command window. Defaults to 0.1.
            delay_between_attempts_s (int, optional): If the command is attempted multiple times delay between attempts. Defaults to 5.
            number_of_attempts (int, optional): How many attempts it will retry the command. This is not done for motion commands incase it moves repeatably. Defaults to 5.
        """
        self.piezo_driver_target = piezo_driver_target
        self.piezo_address = piezo_address
        self.piezo_stage = piezo_stage
        self.temperature_kelvin = temperature_kelvin
        self.frequency_hz = frequency_hz
        self.relative_step_size_percent = relative_step_size_percent
        self.torque_factor = torque_factor
        self.cacli_version = cacli_version
        self.time_out = time_out
        self.delay_between_attempts_s = delay_between_attempts_s
        self.number_of_attempts = number_of_attempts

    #########################################################################################################################################################################    
    # Implementation of the abstract signal generator functions 
    #########################################################################################################################################################################    

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
        piezo_driver_target = self.piezo_driver_target
        piezo_address = self.piezo_address
        piezo_stage = self.piezo_stage
        temperature_kelvin = self.temperature_kelvin
        frequency_hz = self.frequency_hz
        relative_step_size = self.relative_step_size_percent
        version = self.cacli_version

        
        if self.torque_factor <=30 and self.torque_factor >= 1:
            trqfr = self.torque_factor
        else:
            raise ValueError(f"TRQFR must be set between 1 and 30  as well as being an integer you entered {trqfr}")

        # Chooses the versions commands 
        match version:
            case CacliVersion.v6:
                command = f"cacli @{piezo_driver_target} MOV {piezo_address} {piezo_stage} {temperature_kelvin} {direction} {frequency_hz} {relative_step_size} {steps} {trqfr}"
            case CacliVersion.v7:
                command = f"cacli @{piezo_driver_target} MOV {piezo_address} {direction} {frequency_hz} {relative_step_size} {steps} {temperature_kelvin} {piezo_stage} {trqfr}"
            case _:
                raise NotImplemented(f"The cacli version {version.name} has not been implemented yet")
        
        response = self.cacli_command(command)

        return response

    def stop_positioner(self,normal_output=True):
        """
        Emergency stop all piezos in motion
        """
        piezo_driver_target = self.piezo_driver_target
        piezo_address = self.piezo_address

        command = f"cacli @{piezo_driver_target} STP {piezo_address}"

        if normal_output:

            response = self.cacli_command(command)
            return response
        else:
            #This is to mute the response for use with the GUI
            self.cacli_command(command)
            return None

        
    # For a connected device there isn't much to check with a third party controlled device 
    def make_connection(self):
        if not self.check_cacli_connection():
            raise Exception(f"Failed to connect to specified device target: {self.piezo_driver_target}")
        
    def close_connection(self):
        pass
    

    #########################################################################################################################################################################    
    # Base Commands 
    #########################################################################################################################################################################    
    def cacli_command(self,command,retry_after_failure=False):
        for n in range(self.number_of_attempts):
            try:
                p = Popen(command.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output, err = p.communicate(b"input data that is passed to subprocess' stdin",timeout=self.time_out)
                return output.decode("utf-8")
            except Exception as e:
                print(e)
                if retry_after_failure:
                    time.sleep(self.delay_between_attempts_s)
                else:
                    # There is a error with certain commands like MOV for newer CLI programs by JPE that means the command line may not receive an exit to new line 
                    # This means that it will never time out because it maintains a open line so if we want to continue this must be timed out 
                    # This is unfortunately not something we are likely able to fix 
                    return -1
                
        raise Exception(f"Failed to execute {command} after {self.number_of_attempts} attempts")
        
    def check_cacli_connection(self):
        
        # call command
        command =  "cacli /USB"

        response = self.cacli_command(command, retry_after_failure=True)
        
        # check if controller id is connected 
        if self.piezo_driver_target in response:
            target_connected = True
        else:
            target_connected = False
            
        return target_connected


    def __repr__(self):
        return f"Target Id: {self.piezo_driver_target}\nAddress: {self.piezo_address}\nStage: {self.piezo_stage}"



if __name__ == "__main__":
    # piezo_driver_target = '1038E201905-12'

    # outer_a_jpe = CacliJpeCadm2(piezo_driver_target = piezo_driver_target,
    #                           piezo_address = 1,
    #                           piezo_stage = "CLA2603",
    #                           temperature_kelvin = 300,
    #                           frequency_hz = 250,
    #                           relative_step_size_percent = 100,
    #                           delay_between_attempts_s = 2)
    
    # outer_a_jpe.time_out = 2
    
    
    # outer_a_jpe.move_positioner(1,200)
    dir = r"C:\Users\LTSPM2\Documents\GitHub\LTSPM2_Interfaces\experimental_configuration\third_party_command_line_interfaces\CPSC_v7.3.20210802"
    cmd = ".\cacli.exe MOV 1 1 250 100 100 300 CLA2603 1"

    import subprocess
    p = subprocess.Popen([".\calci.exe", "/USB"], cwd=dir)
    p.wait()