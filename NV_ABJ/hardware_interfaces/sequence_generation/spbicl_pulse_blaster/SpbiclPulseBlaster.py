import subprocess
from tempfile import TemporaryDirectory
from os.path import join

from NV_ABJ import PulseGenerator

class SpbiclPulseBlaster(PulseGenerator):
    def __init__(self,clock_frequency_megahertz:int=500, maximum_step_time_s:float = 6.9):
        """This class interfaces with the pulse blaster using the command line interpreter provided by 
        SpinCore as an exe "spbicl.exe" 

        Args:
            devices (list): list of sequence controlled devices 
            clock_frequency_megahertz (float, optional): What the pulse blaster will be set to. Defaults to 500.
            maximum_step_time_s (float, optional): This is the maximum time a step can take if it is longer it will be broken into n steps 
        """
        self.clock_frequency_megahertz = clock_frequency_megahertz
        self.maximum_step_time_s = maximum_step_time_s
        self._locked_commands = False
    
    def load_sequence(self, sequence:str)->int:
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
        if not self._locked_commands:
            print(devices)
        else:
            raise Warning("To update devices you must stop the sequence")
    
    def generate_sequence(self,sequence_class)->str:
        """This function takes the sequence class and converts it into a format that can be interpreted by the pulse blaster 

        Args:
            sequence_class (_type_): _description_

        Returns:
            str: This returns a string that can be used to load the sequence into the pulse blaster 
            This command is going to commonly be followed by load(sequence) they are kept separate because load 
            is a more general function and you may want to generate sequences and save them without 
        """
        ...
    

    

if __name__ == "__main__":


    pbi = SpbiclPulseBlaster(None)
    print(pbi.start())
    print(pbi.stop())
    print(pbi.clear())





