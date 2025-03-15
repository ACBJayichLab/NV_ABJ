"""

"""
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
from os.path import join


class SpbiclPulseBlaster:
    """
    This class interfaces with the pulse blaster using the command line interpruter provided by 
    SpinCore as an exe "spbicl.exe" 
    """
    def __init__(self,sequence_text:str,clock_frequency_megahertz:float=500,sequence_class=None):
        self.sequence_text = sequence_text
        self.clock_frequency_megahertz = clock_frequency_megahertz
        self.sequence_class = sequence_class
    
    def load_sequence(self):
        """
        spbicl load file.pb 100.0 Load file.pb at 100 MHz
        """  

        # Creates a directory we can write a pulse sequence into 
        with tempfile.TemporaryDirectory(prefix="pulse_sequence_") as temp_directory:
            sequence_file_path = join(temp_directory,"__temporary_pulse_blaster_loading_sequence__.pb")

            # writing the pulse sequence into the directory it has to close before we can use the file in the SpinCore CLI
            with open(sequence_file_path,"w") as file:
                file.write(self.sequence_text)

            # Running the load command for spincore cli
            command = f"spbicl load {str(sequence_file_path)} {str(self.clock_frequency_megahertz)}"
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

        if response == -1:
            raise Exception("Failed to load program to pulse blaster")
               
        return response

    def load_and_start(self):
         # Creates a directory we can write a pulse sequence into 
        with tempfile.TemporaryDirectory(prefix="pulse_sequence_") as temp_directory:
            sequence_file_path = join(temp_directory,"__temporary_pulse_blaster_loading_sequence__.pb")

            # writing the pulse sequence into the directory it has to close before we can use the file in the SpinCore CLI
            with open(sequence_file_path,"w") as file:
                file.write(self.sequence_text)

            # Running the load command for spincore cli
            command = f"spbicl load {str(sequence_file_path)} {str(self.clock_frequency_megahertz)}"
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

            

        if response == -1:
            raise Exception("Failed to load program to pulse blaster")
               
        else:
            # with this started successfully we can start the sequence 
            command = ["spbicl","start"]        
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)
            return response
        
    def start(self):
        """
        starts the loaded sequence 

        spbicl start Start program execution
        """
        command = ["spbicl","start"]        
        response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return response
    
    def stop(self):
        """
        stops pulseblaster sets all values to zero
        
        spbicl stop Stop program execution
        """
        command = ["spbicl","stop"]
        response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return response

    def stop_clear(self):
        """
        clears pulse blaster sequence by loading an empty sequence to the 
        pulse blaseter and stops the sequence         
        """
        empty_sequence = "start: 0b0000 0000 0000 0000 0000 0000, 1 s, branch, start"
                
        # stops the sequence
        response = self.stop()
        if response == 0:
            # Creates a directory we can write a pulse sequence into 
            with tempfile.TemporaryDirectory(prefix="pulse_sequence_") as temp_directory:
                sequence_file_path = join(temp_directory,"__temporary_pulse_blaster_loading_sequence__.pb")

                # writing the pulse sequence into the directory it has to close before we can use the file in the SpinCore CLI
                with open(sequence_file_path,"w") as file:
                    file.write(empty_sequence)

                # Running the load command for spincore cli
                command = f"spbicl load {str(sequence_file_path)} {str(self.clock_frequency_megahertz)}"
                response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

                
            if response == -1:
                raise Exception("Failed to load program to pulse blaster")
                
            return response

        else:
            raise Exception("Failed to stop pulse sequence")
    
    def clear(self):
        """
        Becuase this is a safeguard step so start doesn't load an old program it is made to be asynchronous so that it won't lead to any issues 
        when implimented with a gui
        """
        empty_sequence = "start: 0b0000 0000 0000 0000 0000 0000, 1 s, branch, start"
        with tempfile.TemporaryDirectory(prefix="pulse_sequence_") as temp_directory:
            sequence_file_path = join(temp_directory,"__temporary_pulse_blaster_loading_sequence__.pb")

            # writing the pulse sequence into the directory it has to close before we can use the file in the SpinCore CLI
            with open(sequence_file_path,"w") as file:
                file.write(empty_sequence)

            # Running the load command for spincore cli
            command = f"spbicl load {str(sequence_file_path)} {str(self.clock_frequency_megahertz)}"
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

            
        if response == -1:
            raise Exception("Failed to load program to pulse blaster")
        else:
            return response

    
    @classmethod
    def from_pulse_sequence_class(cls,sequence_class):
        return cls(sequence_class.make_sequence(),sequence_class.clock_frequency_megahertz,sequence_class)
    
    @classmethod
    def sequence_from_file(cls,file_path,values_dict,clock_frequency_megahertz):
        """
        This operates just as a simple replace command for example in the pulse sequence file 
        we should write $variable = variable_val where variable_val will be replaced for the 
        actual value
        
        PBI.sequence_from_file(file_path=r"C:/...",values_dict={"variable_val_1":19,"variable_val_1":52})
        """
        
        with open(file_path,"r") as file:
            sequence_text = file.read()

        for variable in values_dict:
            sequence_text = sequence_text.replace(variable,values_dict[variable])

        return cls(sequence_text,clock_frequency_megahertz)


class PulseSequenceVisulizer:
    def __init__(self,pulse_sequence_class=None,pulse_sequence_text=None):
        self.pulse_sequence_class = pulse_sequence_class
        self.pulse_sequence_text = pulse_sequence_text

    @classmethod
    def from_pulse_sequence_class(cls):
        return cls(...)
    
    @classmethod
    def from_pulse_blaster_file(cls):
        return cls(...)

if __name__ == "__main__":

    # import time

    # # Making a basic sequence
    # GreenAOM = PulseBlasterControlled("GreenAOM",0)
    # RfSwitch = PulseBlasterControlled("RfSwitch",2)

    # seq = PulseBlasterSequence(clock_frequency_megahertz=100)
    
    # # seq.add_step(None,100)
    # # seq.add_step([GreenAOM,RfSwitch],200,"ns")

    # seq.add_step([GreenAOM],500,"ms")
    # seq.add_step([],500,"ms")
    
    # # seq.add_step([],400,"ms")
    # # seq.add_step([RfSwitch],500,"s")
    # # Loading a pulse sequence 
    # print(seq)
    # pbi = PulseBlasterInterfaceCLI.from_pulse_sequence_class(sequence_class=seq)
    # response = pbi.load_and_start()
    # time.sleep(5)

    # pbi.clear()

    # # gives time to wait for the program to finish. When implemented in a gui the run time continues and this is done elsewhere on the computer
    # time.sleep(10)

    

    # # response = pbi.stop_clear()
    # # print(response)

    print(pb.pb_count_boards())
    print(pb.pb_init())





