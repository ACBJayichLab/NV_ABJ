__all__ = ["SpbiclPulseBlaster"]

import subprocess
from tempfile import TemporaryDirectory
from os.path import join

from NV_ABJ import seconds 
from NV_ABJ.abstract_interfaces.pulse_generator import PulseGenerator
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import *

class SpbiclPulseBlaster(PulseGenerator):
    def __init__(self,clock_frequency_megahertz:int=500, maximum_step_time_s:float = 5,available_ports:int=23):
        """This class interfaces with the pulse blaster using the command line interpreter provided by 
        SpinCore as an exe "spbicl.exe" 

        Args:
            devices (list): list of sequence controlled devices 
            clock_frequency_megahertz (float, optional): What the pulse blaster will be set to. Defaults to 500.
            maximum_step_time_s (float, optional): This is the maximum time a step can take if it is longer it will be broken into n steps 
            available_ports (int, optional): How many bits the pulse blaster can control. Defaults to 23
        """
        self.clock_frequency_megahertz = clock_frequency_megahertz
        self.maximum_step_time_s = maximum_step_time_s
        self.available_ports = available_ports
        self._locked_commands = False
    
    def make_connection(self):
        # This is handled by spbicl.exe
        pass
    def close_connection(self):
        # This is handled by spbicl.exe
        pass
    
    def load(self, sequence:str)->int:
        """
        This loads a sequence into the pulse blaster. The sequence is the same as the basic file format you upload using a
        spin core file format 

        Args:
            sequence(str): string formatted in the style of a sequence file. Loading a empty string will clear the pulse blaster

        example of sequence:
        
            label: 0b1111 1111 1111 1111 1111 1111, 500 ms
                   0b0000 0000 0000 0000 0000 0000, 500 ms, branch, label

        Returns:
            int: This is zero that indicates correct loading and -1 if it failed to load to the device other errors may have different numbers
        """  
        # Creates a temporary directory 
        with TemporaryDirectory(prefix="pulse_sequence_") as temp_directory:
            sequence_file_path = join(temp_directory,"__temporary_pulse_blaster_loading_sequence__.pb")

            # writing the pulse sequence into the directory it has to close before we can use the file in the SpinCore CLI
            with open(sequence_file_path,"w") as file:
                file.write(sequence)

            # Running the load command for spincore cli
            command = f"spbicl load {str(sequence_file_path)} {str(self.clock_frequency_megahertz)}"
            response = subprocess.call(command,stdout = subprocess.DEVNULL)#, stderr=subprocess.STDOUT)

        if response == -1:
            raise Exception("Failed to load program to pulse blaster")
        elif response == 4294967295:
            raise ValueError("Incorrect formatting in file or command structure")
        else:
            return response
        
    def start(self)->int:
        """
        starts the loaded sequence 

        spbicl start Start program execution

        Returns:
            int: This is zero that indicates correct starting and -1 if it failed to load to the device other errors may have different numbers
        """
        command = ["spbicl","start"]        
        response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # Prevents updating devices until stopped 
        self._locked_commands = True
        
        if response != 0:
            raise Exception("Failed to start program to pulse blaster")
        else:
            return response
    
    def stop(self)->int:
        """
        stops pulseblaster sets all values to zero
        
        spbicl stop Stop program execution

        Returns:
            int: This is zero that indicates correct stopping and -1 if it failed to load to the device other errors may have different numbers
       
        """
        command = ["spbicl","stop"]
        response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # Unlocks commands for other items 
        self._locked_commands = False
        
        if response != 0:
            raise Exception("Failed to stop program to pulse blaster")
        else:
            return response
    
    def clear(self)->int:
        """
        To clear we load an empty string into the load sequence 
        
        Returns:
            int: This is zero that indicates correct loading and -1 if it failed to load to the device other errors may have different numbers
       
        """
        empty_sequence = ""

        if not self._locked_commands:
            response = self.load_sequence(sequence=empty_sequence)
            return response   
        
        else:
            raise Warning("To clear sequence you must stop the sequence")

    def update_devices(self, devices:list)->int:
        """Takes a list of sequence controlled devices and creates a sequence loads it into the pulse blaster and starts it 

        Args:
            devices (list): This is a list of sequence controlled devices 

        Raises:
            Warning: If the pulse blaster is running it will not let you load a sequence this is to prevent errors where a sequence is stopped during a 
            measurement 

        Returns:
            int: _description_
        """
        if not self._locked_commands:
            seq = Sequence()
            # Uses a default timing of 1 this will be replaces later but prevents the duration error 
            devices_on = []
            for dev in devices:
                if dev.device_status:
                    devices_on.append(dev)
            seq.add_step(devices=devices_on, duration=1)
            seq_text = self.generate_sequence(seq)

            self.load(sequence=seq_text)
            response = self.start()
            return response

        else:
            raise Warning("To update devices you must stop the sequence")

    
    def generate_sequence(self,sequence_class:Sequence)->str:
        """This function takes the sequence class and converts it into a format that can be interpreted by the pulse blaster 

        Args:
            sequence_class (Sequence): A sequence of the devices and times you wish to add

        Returns:
            str: This returns a string that can be used to load the sequence into the pulse blaster 
            This command is going to commonly be followed by load(sequence) they are kept separate because load 
            is a more general function and you may want to generate sequences and save them without 
        """       
        sequence_text = ""
        # Gets a linear time sequence from the sequence generation class
        instructions, sub_routines = sequence_class.instructions(wrapped=True,allow_subroutine=False)
        sequence_length = len(instructions)-1

        for ind, seq in enumerate(instructions):
            # Checks if it is a
            if not instructions[seq][0]:
                duration_ns = instructions[seq][1][0]
                device_addresses = instructions[seq][1][1]
            
                if duration_ns > self.maximum_step_time_s/seconds.ns.value:
                    raise EncodingWarning(f"Can not enter a time longer than the pulse blaster maximum step time {self.maximum_step_time_s}")

                binary = 0
                for dev_add in device_addresses:
                    binary = binary + pow(10,dev_add)              

                address_line = str(111)+str(binary).zfill(self.available_ports-2)

                if sequence_length == 1:
                    return f"Start: 0b{address_line}, {duration_ns} ns, branch, Start"
                
                else:
                    if ind == 0 and sequence_length > 0:
                        line = f"Start: 0b{address_line}, {duration_ns} ns\n"
                    elif ind == 0 and sequence_length == 0:
                        line = f"Start: 0b{address_line}, {duration_ns} ns, branch, Start"         
                    elif ind > 0 and ind < sequence_length:          
                        line = f"       0b{address_line}, {duration_ns} ns\n"
                    elif ind == sequence_length:
                        line = f"       0b{address_line}, {duration_ns} ns, branch, Start"
                    else:
                        raise EncodingWarning(f"Could not generate sequence failed with index:{ind}, Sequence Length: {sequence_length}")  

                sequence_text = sequence_text + line

            # We need to add the sub routines 
            else:
                sub_routine = sub_routines[instructions[seq][1]]
                repetitions = instructions[seq][2]

                sr_len = len(sub_routine)-1

                ind_temp = ind

                for sr_ind,sr in enumerate(sub_routine):
                    
                    duration_ns = sr[0]
                    device_addresses = sr[1]

                    binary = 0
                    for dev_add in device_addresses:
                        binary = binary + pow(10,dev_add)

                    if duration_ns > self.maximum_step_time_s/seconds.ns.value:
                        raise EncodingWarning(f"Can not enter a time longer than the pulse blaster maximum step time for sub sequence {self.maximum_step_time_s}")

                    address_line = str(111)+str(binary).zfill(self.available_ports-2)


                    if ind_temp == 0 and sr_ind == 0:
                        line = f"Start: 0b{address_line}, {duration_ns} ns, loop, {repetitions}\n" 
                        ind_temp = ind_temp + 1   
                    
                    elif ind_temp > 0 and sr_ind == 0:
                        line = f"       0b{address_line}, {duration_ns} ns, loop, {repetitions}\n"

                    elif ind_temp > 0 and ind < sequence_length and sr_ind > 0 and sr_ind < sr_len:
                        line = f"       0b{address_line}, {duration_ns} ns\n" 

                    elif ind_temp > 0 and ind < sequence_length and sr_ind == sr_len:
                        line = f"       0b{address_line}, {duration_ns} ns, end_loop\n" 

                    elif ind_temp == sequence_length and sr_ind == sr_len:
                        line = f"       0b{address_line}, {duration_ns} ns, end_loop, branch, Start"  
                    else:
                        raise EncodingWarning(f"Failed:\n sub routine index:{sr_ind}, sequence_index: {ind},\n sub routine length: {sr_len}, sequence length: {sequence_length}")


                    sequence_text = sequence_text + line
            
        return sequence_text
        
            
      


# # # # # ##############################################################################################################
# # # # # #     _    _
# # # # # #    (o)--(o)
# # # # # #   /.______.\
# # # # # #   \________/
# # # # # #  ./        \.
# # # # # # ( .        , )
# # # # # #  \ \_\\//_/ /
# # # # # #   ~~  ~~  ~~ The frog of linear timing 
# # # # # ##############################################################################################################

