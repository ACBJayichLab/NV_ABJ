"""
This is a class that is based on interactions with the provided Cacli.exe file from JPE in order to use this you must add the location of the Cacli.exe
folder to the system enviroment variables for example if you saved it to "C:" you would add "C:" to the system variables path
"""
import json
import subprocess
import os

class CacliJpe:

    def __init__(self,piezo_driver_target,piezo_address,piezo_stage):
        self.piezo_driver_target = piezo_driver_target
        self.piezo_address = piezo_address
        self.piezo_stage = piezo_stage

    
    def move(self,temperature,direction, frequency,relative_step_size, steps, trqfr):
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

        # call command
        #command =  ["cacli", str("@"+self.piezo_driver_target),"MOV", self.piezo_address,self.piezo_stage, temperature,direction,frequency,relative_step_size,steps,trqfr]
        #response = subprocess.check_output(command)

        command = f"cacli @{self.piezo_driver_target} MOV {self.piezo_address} {self.piezo_stage} {temperature} {direction} {frequency} {relative_step_size} {steps} {trqfr}"
        response = subprocess.call(command)
        

        return response

    def stop(self,normal_output=True):
        """
        Emergancy stop all piezos in motion
        """
        # command = ["cacli","STP",self.piezo_address]
        # response = subprocess.check_output(command)

        command = f"cacli @{self.piezo_driver_target} STP {self.piezo_address}"

        if normal_output:
            response = subprocess.call(command)
            return response
        else:
            #This is to mute the response for use with the GUI
            subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            return None

        


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

    def __repr__(self):
        return f"Target Id: {self.piezo_driver_target}\nAddress: {self.piezo_address}\nStage: {self.piezo_stage}"

    @classmethod
    def import_config_file(cls,file_path):
        with open(file_path,'r') as file:
            data = json.load(file)
        
        piezo_driver_target = data["target"]
        piezo_driver_target_type = data["target_type"]
        piezo_address = data["address"]
        piezo_stage = data["stage"]
        return cls(piezo_driver_target,piezo_driver_target_type,piezo_address,piezo_stage)




if __name__ == "__main__":

    confirm_movement = input("About to move JPEs as a test make sure this is a safe procedure\nWould you like to continue[y/n]")
    if confirm_movement == "y" or confirm_movement == "Y":
        import time

        print("Moving")
        target_id = "1038E201905-14"
        piezo_address = 3
        piezo_stage = "CS021-RLS.Z"


        InnerZ_JPE = JpeMovement(piezo_driver_target=target_id,piezo_address=piezo_address,piezo_stage=piezo_stage)

        print(InnerZ_JPE.move(temperature="300",direction="0", frequency="200",relative_step_size="75", steps="1000", trqfr="1.0"))

        time.sleep(.25)
        InnerZ_JPE.stop()
        time.sleep(1)
        print(InnerZ_JPE.move(temperature="300",direction="1", frequency="200",relative_step_size="75", steps="1000", trqfr="1.0"))

        time.sleep(.25)
        InnerZ_JPE.stop(normal_output=False)
        print(InnerZ_JPE)
    
        print(InnerZ_JPE.check_cacli_connection())
    else:
        print("Cancelling Movement")

