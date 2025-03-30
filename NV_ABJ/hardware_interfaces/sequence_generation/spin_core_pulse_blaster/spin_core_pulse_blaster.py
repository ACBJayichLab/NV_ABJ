from spinapi import *

from NV_ABJ import PulseGenerator

class SpinCorePulseBlasterEsrPro(PulseGenerator):
    def __init__(self,clock_frequency_megahertz:int=500, maximum_step_time_s:float = 6.9,board_number:int=0):
        """This class interfaces with the pulse blaster using the command line interpreter provided by 
        SpinCore as an exe "spbicl.exe" 

        Args:
            devices (list): list of sequence controlled devices 
            clock_frequency_megahertz (float, optional): What the pulse blaster will be set to. Defaults to 500.
            maximum_step_time_s (float, optional): This is the maximum time a step can take if it is longer it will be broken into n steps 
            board (int, optional): This is the board number if you have multiple installed 
        """
        self.clock_frequency_megahertz = clock_frequency_megahertz
        self.maximum_step_time_s = maximum_step_time_s
        self.board_number = board_number
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
        # Indicate we are starting programming the sequence  
        pb_start_programming(PULSE_PROGRAM)

        # start of program pb_inst_pbonly(ON | pins on, state of CONTINUE, branching to line, duration)
        start = pb_inst_pbonly(ON | 0xE, CONTINUE, 0, 40.0 * ns)

        # Going through all sequences between start and end 

        # Looping back to start of sequence 
        pb_inst_pbonly(0, BRANCH, start, 40.0 * ns)



        pb_stop_programming() # Finished sending instructions
        pb_reset()
        
    def start(self)->int:
        """
        starts the loaded sequence 

        spbicl start Start program execution

        Returns:
            int: This is zero that indicates correct starting and -1 if it failed to load to the device other errors may have different numbers
        """
        if (response := pb_start()) != 0:
            raise Exception("Error occurred trying to trigger board: %s\n" % pb_get_error())
        
        return response
        
    
    def stop(self)->int:
        """
        stops pulseblaster sets all values to zero
        
        spbicl stop Stop program execution

        Returns:
            int: This is zero that indicates correct stopping and -1 if it failed to load to the device other errors may have different numbers
        """
    
        if (response:=pb_stop()) !=0:
            raise Exception("Error occurred trying to stop board: %s\n" % pb_get_error)
        return response
    
    def clear(self)->int:
        """
        To clear we load an empty string into the load sequence 
        
        Returns:
            int: This is zero that indicates correct loading and -1 if it failed to load to the device other errors may have different numbers
       
        """
       

    def update_devices(self, devices:list)->int:
        if not self._locked_commands:
            print(devices)
        else:
            raise Warning("To update devices you must stop the sequence")
    
    def generate_sequence(self,sequence_class)->list:
        """This function takes the sequence class and converts it into a format that can be interpreted by the pulse blaster 

        Args:
            sequence_class (_type_): _description_

        Returns:
            str: This returns a string that can be used to load the sequence into the pulse blaster 
            This command is going to commonly be followed by load(sequence) they are kept separate because load 
            is a more general function and you may want to generate sequences and save them without 
        """
        # Converting to hex for the pulse blaster 
        def binary_to_hex(n):
            hex_num = hex(int(str(n), 2))
            return(hex_num)
        def bit_location_to_binary(loc)->int:
            return int(pow(10,loc))
        
        durations = []
        devices = []

        for sub in sequence_class.sequence_subsets:
            times_looped = sub.loop_steps
            for i in range(times_looped):

                # Gets the devices numbers 
                for step in sub.steps:
                    number = 0
                    for dev in step["devices"]:
                        number = number + bit_location_to_binary(dev.address)
                    
                    hex_number = binary_to_hex(number)
                    if "2" not in str(hex_number):
                        devices.append(hex_number)
                    else:
                        raise ValueError(f"Devices can not have the same address {binary_to_hex(number)} there should only be 1 and 0")






        for item in self.steps:
            devices = []
            if item["devices"] != None:
                for dev in item["devices"]:
                    devices.append(dev.device_label)

            response = response + f"    devices on:{devices}, duration of step: {item["duration_s"]} s\n"


        
    
    def make_connection(self):
        pb_select_board(self.board_number)# Selects the board when you initialize the class 
        if pb_init() != 0:
            raise Exception("Could not initialize board: %s" % pb_get_error())

        pb_core_clock(self.clock_frequency_megahertz)
        

    def close_connection(self):
        # Closes connection with pulse blaster
        pb_close()


    @property
    def device_configuration(self):
        return self.board_number,self.clock_frequency_megahertz
    
    def __repr__(self):
        return f"The board selected is{self.board_number} and is set to {self.clock_frequency_megahertz} MHz"
