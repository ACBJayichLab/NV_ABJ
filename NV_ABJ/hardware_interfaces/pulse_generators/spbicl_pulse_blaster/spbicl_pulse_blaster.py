import subprocess
from tempfile import TemporaryDirectory
from os.path import join
import multiprocessing
import time
# Importing abstract class and units 
from NV_ABJ import PulseGenerator,seconds

# Importing sequence 
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence, SequenceDevice


class SpbiclPulseBlaster(PulseGenerator):
    def __init__(self,spbicl_path:str=None,controlled_devices:list=None,clock_frequency_megahertz:int=500, maximum_step_time_s:float = 5,available_ports:int=23):
        """This class interfaces with the pulse blaster using the command line interpreter provided by 
        SpinCore as an exe "spbicl.exe" 

        Args:
            spbicl_path (str, optional): path to the spbicl.exe program. When set to None you must have the spbicl in your enviroment variables 
            clock_frequency_megahertz (float, optional): What the pulse blaster will be set to. Defaults to 500.
            maximum_step_time_s (float, optional): This is the maximum time a step can take if it is longer it will be broken into n steps 
            available_ports (int, optional): How many bits the pulse blaster can control. Defaults to 23
        """
        self.spbicl_path = spbicl_path
        self.clock_frequency_megahertz = clock_frequency_megahertz
        self.maximum_step_time_s = maximum_step_time_s
        self.available_ports = available_ports
        self.controlled_devices = controlled_devices
        self._locked_commands = False
    
    def _start_asynchronous_worker(self,delayed_s:float):
        # Wait for a time
        print("Waiting Time")
        time.sleep(delayed_s)

        # Call start function
        self.start()
        print("Starting Function")



    def start_asynchronous(self, delayed_s:float)->None:
        """ This function calls the start function after the specified amount of time
        This is used so that the timing of the first pulse can start after the counters are loaded.
        This allows for the timing of the devices to not be inhibited for determining when the first pulse 
        was performed. N

        Needed for non-uniform pulses a.k.a. pulses with multiple different readouts 
        
        Args:
            delayed_s(float): How long the function will wait before starting the pulse blaster
        """
        start_async = multiprocessing.Process(target=self._start_asynchronous_worker, args=(delayed_s,))
        start_async.start()

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

            if self.spbicl_path == None:
                response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

            else:
                command = ".\\"+command
                response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True, cwd=self.spbicl_path)

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
        if self.spbicl_path == None:
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

        else:
            command[0] = ".\\"+command[0]
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True, cwd=self.spbicl_path)
        
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
        if self.spbicl_path == None:
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)

        else:  
            command[0] = ".\\"+command[0]
            response = subprocess.call(command,stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True, cwd=self.spbicl_path)
        
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
        empty_sequence = "label: 0b0000 0000 0000 0000 0000 0000, 500 ms, branch, label"

        if not self._locked_commands:
            response = self.load(sequence=empty_sequence)
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
                seq.devices.add(dev.config)
                if dev.device_status:
                    devices_on.append(dev)

            seq.add_step(devices=devices_on, duration_ns=1e9)

            if self.controlled_devices != None:
                seq.add_devices(self.controlled_devices)

            seq_text = self.generate_sequence(seq)
            # If no devices are on we want to clear the output
            if len(devices_on) == 0:
                self.clear()

            self.load(sequence=seq_text)
            response = self.start()
            return response

        else:
            raise Warning("To update devices you must stop the sequence")

    
    def generate_sequence(self,sequence_class:Sequence,wrapped=True,allow_subroutine=True)->str:
        """This function takes the sequence class and converts it into a format that can be interpreted by the pulse blaster 

        Args:
            sequence_class (Sequence): A sequence of the devices and times you wish to add

        Returns:
            str: This returns a string that can be used to load the sequence into the pulse blaster 
            This command is going to commonly be followed by load(sequence) they are kept separate because load 
            is a more general function and you may want to generate sequences and save them without 
        """       
        sequence_text = ""
        
        # If the user has defined all controlled devices and would like to have the pulse blaster control for inverted ports
        if self.controlled_devices != None:
            sequence_class.add_devices(self.controlled_devices)

        # Gets a linear time sequence from the sequence generation class
        instructions, sub_routines = sequence_class.instructions(wrapped=wrapped,allow_subroutine=allow_subroutine)

        sequence_length = len(instructions)-1

        def addresses_to_line(device_addresses:list):
            binary = 0
            for dev_add in device_addresses:
                binary = binary + pow(10,dev_add)              

            address_line = str(111)+str(binary).zfill(self.available_ports-2)
            return address_line

        for ind, seq in enumerate(instructions):
            
            # Checks if it is not a sub routine requiring a more complex process
            if not instructions[seq][0]:
                duration_ns = instructions[seq][1][0]
            
                address_line = addresses_to_line(device_addresses=instructions[seq][1][1])

                if ind == 0:
                    starting_condition = "Start: "  
                else:
                    starting_condition = "       "

                if ind == sequence_length:
                    end_condition = ", branch, Start"
                else:
                    end_condition = ""

                if sequence_length == 0:
                    duration = self.maximum_step_time_s/seconds.ns.value
                
                if duration_ns > self.maximum_step_time_s/seconds.ns.value:
                    if (remainder_duration := int(duration_ns%(self.maximum_step_time_s/seconds.ns.value))) == 0:
                        duration = self.maximum_step_time_s/seconds.ns.value
                        duration_ns = duration_ns - (self.maximum_step_time_s/seconds.ns.value)
                    else:
                        duration = remainder_duration
                else:
                    duration = duration_ns
               
                line = f"{starting_condition}0b{address_line}, {duration} ns{end_condition}\n"
                sequence_text = sequence_text + line

                while duration_ns > self.maximum_step_time_s/seconds.ns.value:
                    duration_ns = duration_ns - self.maximum_step_time_s/seconds.ns.value
                    line = f"       0b{address_line}, {self.maximum_step_time_s/seconds.ns.value} ns\n"
                    sequence_text = sequence_text + line

            # We need to add the sub routines 
            else:
                sub_routine = sub_routines[instructions[seq][1]]
                repetitions = instructions[seq][2]

                sr_len = len(sub_routine)-1

                for sr_ind,sr in enumerate(sub_routine):
                    
                    duration_ns = sr[0]

                    address_line = addresses_to_line(device_addresses=sr[1])

                    if ind == 0 and sr_ind == 0:
                        starting_condition = "Start: "
                    else:
                        starting_condition = "       "

                    if sr_ind == 0:
                        end_condition = f", loop, {repetitions}"
                    else:
                        end_condition = ""
                    
                    if sr_ind == sr_len:
                        end_condition = ", end_loop"

                    if ind == sequence_length and sr_ind == sr_len:
                        end_condition = end_condition + ", branch, Start"

                    if sequence_length == 0:
                        duration = self.maximum_step_time_s/seconds.ns.value
                    
                    if duration_ns > self.maximum_step_time_s/seconds.ns.value:
                        if (remainder_duration := int(duration_ns%(self.maximum_step_time_s/seconds.ns.value))) == 0:
                            duration = self.maximum_step_time_s/seconds.ns.value
                            duration_ns = duration_ns - (self.maximum_step_time_s/seconds.ns.value)
                        else:
                            duration = remainder_duration
                    else:
                        duration = duration_ns

                
                    line = f"{starting_condition}0b{address_line}, {duration} ns{end_condition}\n"
                    sequence_text = sequence_text + line

                    while duration_ns > self.maximum_step_time_s/seconds.ns.value:
                        duration_ns = duration_ns - self.maximum_step_time_s/seconds.ns.value
                        line = f"       0b{address_line}, {self.maximum_step_time_s/seconds.ns.value} ns\n"
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
# # # # # #
# # # # # #
# # # # # #     .----.   @   @
# # # # # #    / .-"-.`.  \v/
# # # # # #    | | '\ \ \_/ )
# # # # # #  ,-\ `-.' /.'  /
# # # # # # '---`----'----' Art by Hayley Jane Wakenshaw
# # # # # ##############################################################################################################

if __name__ == "__main__":
    from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import SequenceDevice
    import time 
    from experimental_configuration import *
    d1 = SequenceDevice(config={"address":0,
                                            "device_label":"AOM Trigger",
                                            "delayed_to_on_ns":0,
                                            "inverted_output":True}
                                    , device_status = True)
    
    d2 = SequenceDevice(config={"address":1,
                                            "device_label":"AOM Trigger",
                                            "delayed_to_on_ns":0,
                                            "inverted_output":True}
                                    , device_status = True)

    d3 = SequenceDevice(config={"address":2,
                                            "device_label":"AOM Trigger",
                                            "delayed_to_on_ns":0,
                                            "inverted_output":False}
                                    , device_status = False)
    
    d4 = SequenceDevice(config={"address":3,
                                            "device_label":"AOM Trigger",
                                            "delayed_to_on_ns":0,
                                            "inverted_output":False}
                                    , device_status = True)
        
    spbicl_path=r"C:\SpinCore\SpinAPI\interpreter"
    pulse_blaster = SpbiclPulseBlaster(spbicl_path=r"C:\SpinCore\SpinAPI\interpreter",controlled_devices=[d1,d2,d3,d4])
    
    dwell_time_s = 30e-3
    
    seq = Sequence()
    seq.add_step(10000,[d1])
    seq_text = pulse_blaster.generate_sequence(sequence_class=seq)
    pulse_blaster.load(sequence=seq_text)
    # pulse_blaster.start()
    print("Starting Async")
    pulse_blaster.start_asynchronous(0.2)
    
    print("loading function")
    with photon_counter_1 as pc:
        print(pc.get_counts_raw(dwell_time_s=dwell_time_s))
    print("Finished Sequence")
    # pulse_blaster.update_devices([d4])


