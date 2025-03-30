from spinapi import *

from NV_ABJ import PulseGenerator, Sequence, SequenceSubset, SequenceDevice, seconds 

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
        
    def load_sequence(self, sequence_class:Sequence)->int:
        """
        This loads a sequence into the pulse blaster. The sequence is the same as the basic file format you upload using a
        spin core file format. This is an early edition where we just fully unwrap the whole sequence no subsets or loops.

        Args:
            sequence(Sequence): Sequence generated from the sequence class. Loading a empty string will clear the pulse blaster
        Returns:
            int: This is zero that indicates correct loading and -1 if it failed to load to the device other errors may have different numbers
        """  
        # Indicate we are starting programming the sequence  
        pb_start_programming(PULSE_PROGRAM)

                # Converting to hex for the pulse blaster 
        def binary_to_hex(n):
            hex_num = hex(int(str(n), 2))
            return(hex_num)
        def bit_location_to_binary(loc)->int:
            return int(pow(10,loc))
        
        units = []
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
                        durations.append(step["duration"])
                        units.append(step["time_unit"])

                    else:
                        raise ValueError(f"Devices can not have the same address {binary_to_hex(number)} there should only be 1 and 0")
                    

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
    
    def generate_sequence(self,sequence_class:Sequence):
        """This function takes the sequence class and converts it into a format that can be interpreted by the pulse blaster 

        Args:
            sequence_class (Sequence): Sequence that has to be generated 

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
        
        sequence_steps = []
        device_address = []
        devices = []

        time_ns = 0

        for sub in sequence_class.sequence_subsets:
            times_looped = sub.loop_steps
            for i in range(times_looped):

                # Gets the devices numbers 
                for step in sub.steps:
                    # We keep track in nano seconds 
                    time_ns = time_ns + step["duration"]*step["time_unit"].value/(seconds.ns.value)
                    
                    for dev in step["devices"]:
                        # Adds the needed parts to the tracking lists
                        if dev.address not in device_address:
                            device_address.append(dev.address)
                            devices.append(dev)
                        
                        sequence_steps.append()

                        number = number + bit_location_to_binary(dev.address)
                        device_on_time_ns = time_ns - dev.delayed_to_on_s
        return 
       
    def make_connection(self):
        # Selecting the board
        pb_select_board(self.board_number)# Selects the board when you initialize the class 
        # Connecting to the pulse blaster
        if pb_init() != 0:
            raise Exception("Could not initialize board: %s" % pb_get_error())
        
        # Setting clock of the pulse blaster
        pb_core_clock(self.clock_frequency_megahertz)
        

    def close_connection(self):
        # Closes connection with pulse blaster
        pb_close()


    @property
    def device_configuration(self):
        return self.board_number,self.clock_frequency_megahertz
    
    def __repr__(self):
        return f"The board selected is{self.board_number} and is set to {self.clock_frequency_megahertz} MHz"
