import subprocess
from tempfile import TemporaryDirectory
from os.path import join

# Importing abstract class and units 
from NV_ABJ import PulseGenerator,seconds

# Importing sequence 
from NV_ABJ.experimental_logic.sequence_generation import Sequence


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

        def adding_lines(ind:int,addresses:int,duration:int,seq_length:int,seq_text:str,operator=111)->str:
            """Used locally to add lines to the sequence 
            Args:
                ind (int): what iteration of the loops we are on/ what line on the string we are writing 
                addresses (int): what binary form of addresses are on
                duration (int): how long in ns it is for
                seq_length (int): how long the overall string we are writing is
                seq_text (str): the string we are writing 

            Returns:
                str: the sequence text string with the appropriate line added 

            Uses a continuous looping method and (branch to start) and uses continue on every line
            """
            addresses = str(operator)+str(addresses).zfill(self.available_ports-2)

            if ind == 0:
                seq_text = seq_text +f"start: 0b{addresses}, {duration} ns\n"
            elif(ind > 0 and ind < seq_length):
                seq_text = seq_text +f"       0b{addresses}, {duration} ns\n"
            else:
                seq_text = seq_text +f"       0b{addresses}, {duration} ns, branch, start"
            
            return seq_text


        # Gets a linear time sequence from the sequence generation class
        linear_time_devices, step_times_ns = sequence_class.linear_time_sequence()
        seq_length = len(step_times_ns)-2 # Checks if the length of a sequence is at least 2 for iteration or 1 for not iteration
        
        # If we have multiple instructions 
        if seq_length > 0:
            sequence_text = ""
            for ind,step_time in enumerate(step_times_ns[:-1]):
                addresses = 0
                for device in sequence_class._devices:
                    if step_time in linear_time_devices[device.address]["on_times_ns"]:
                            addresses = addresses + pow(10,device.address)
                
                # Finds the duration by simple subtraction 
                duration_ns = int(step_times_ns[ind+1]-step_time)
                
                # If the duration is longer than the maximum time for a single step it loops adding steps and subtracting the duration 
                while duration_ns > self.maximum_step_time_s/seconds.ns.value:
                    duration_ns = int(duration_ns - self.maximum_step_time_s/seconds.ns.value)
                    # Adding 1 to sequence length so we don't have issues when a value is maxed out on time and is the end of the sequence
                    sequence_text = adding_lines(ind,addresses,int(self.maximum_step_time_s/seconds.ns.value),seq_length+1,sequence_text)
            
                # Adding the next line to the sequence text and the remainder if there is any from looping 
                sequence_text = adding_lines(ind,addresses,duration_ns,seq_length,sequence_text)
        
        # If there is only one instruction
        elif seq_length == 0:
            # With only one instruction there is no state changes so duration can be the maximum 
            addresses = 0
            for device_address in linear_time_devices:
                    addresses = addresses + pow(10,device_address)

            sequence_text = ""
            # Adds a starting and looping line breaking one instruction into two 
            sequence_text = adding_lines(0,addresses,int(self.maximum_step_time_s/seconds.ns.value),1,sequence_text)
            sequence_text = adding_lines(1,addresses,int(self.maximum_step_time_s/seconds.ns.value),1,sequence_text)
        else:
            raise ValueError("Sequence must contain one or more steps")

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


