__all__ = ["SpbiclPulseBlaster"]

import subprocess
from tempfile import TemporaryDirectory
from os.path import join

from NV_ABJ.abstract_device_interfaces.pulse_generator import PulseGenerator
from NV_ABJ.sequence_generation.sequence_generation import *
from NV_ABJ.units import seconds

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

        def generate_line(binary_address:int,operator=111)->str:
            """generates the bit formulation
            Args:
                binary_address (int): address line
            Returns:
                str: The line made from address and duration
            """

            # Generate the bit line
            address_line = str(operator)+str(binary_address).zfill(self.available_ports-2)
            return address_line


        # Gets a linear time sequence from the sequence generation class
        linear_time_devices, step_times_ns = sequence_class.linear_time_sequence()
        
        seq_length = len(step_times_ns)-2 # Checks if the length of a sequence is at least 2 for iteration or 1 for not iteration

        # If we have multiple instructions 
        if seq_length > 0:
            
            # If we are looping we want to wrap the starting conditions into the end loops to make sure it is continuous 
            if sequence_class.loop_end_condition:
                
                # Finding the time the last devices were turned on 
                final_time_on = 0
                for device_address in linear_time_devices:
                    if final_time_on < (device_final := max(linear_time_devices[device_address]["on_times_ns"])):
                        final_time_on = device_final
                
                # Finding the devices that were on in the end 
                devices_on_in_end = set()
                for device_address in linear_time_devices:
                    if final_time_on == max(linear_time_devices[device_address]["on_times_ns"]):
                        devices_on_in_end.add(device_address)
                
                # Finding devices that have a delayed on and need to be shifted
                total_sequence_time = max(step_times_ns) # Maximum time 
                devices_needing_shift = [] # Devices getting shifted
                shifted_times = [] # Shifted time for the device to be on 
                for device in sequence_class._devices:
                    # If the delay is larger than zero we want to check if it was on in the end 
                    if device.delayed_to_on_s > 0 and device.address not in devices_on_in_end:

                        # Checking if the device needs to be shifted 
                        if (initial := min(linear_time_devices[device.address]["on_times_ns"]))< 0:
                            # If the device was not on we need to add the device to be on at the end but is on before zero 
                            # we must shift it to the end wrapping the times 
                            devices_needing_shift.append(device.address)
                            shifted_times.append(total_sequence_time+initial)



                # For devices that need to be shifted we need to recursively add them in descending order
                if shifted_times != []:
                    sorted_shift = zip(*sorted(zip(shifted_times, devices_needing_shift), reverse=True))
                    
                    # Starting from the longest shift we want to add devices to the sequence 
                    for ind, time,device in enumerate(sorted_shift):
                        for step_time in step_times_ns:
                            # If the time is greater than step times all steps after will require this device on
                            
                            if time >= step_time:
                                # Checking which devices are on at this step time 
                                for device_address in linear_time_devices:
                                    if step_time in linear_time_devices[device_address]["on_times_ns"]:
                                        linear_time_devices[device_address]["on_times_ns"].add(time)


                # Removing any times from the sequence less than zero
                for step_time in step_times_ns:
                    if step_time < 0:
                        step_times_ns.remove(step_time)
            


            # This is a list of tuples (binary devices on, duration)
            sequence_list = []

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
                    sequence_list.append((addresses,int(self.maximum_step_time_s/seconds.ns.value)))
            
                # Adding the next line to the sequence text and the remainder if there is any from looping 
                sequence_list.append((addresses,duration_ns))

            # Iterating through the list looking for any repeating phrases 
            return sequence_list


        
        # If there is only one instruction
        elif seq_length == 0:
            # With only one instruction there is no state changes so duration can be the maximum 
            addresses = 0
            for device_address in linear_time_devices:
                    addresses = addresses + pow(10,device_address)

            sequence_text = f"start: 0b{generate_line(addresses)}, {int(self.maximum_step_time_s/seconds.ns.value)} ns, branch, start"
            return sequence_text
        
        # If there are zero lines in the sequence
        else:
            raise ValueError("Sequence must contain one or more steps")



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


# # from NV_ABJ import SequenceDevice,Sequence,SequenceSubset

pulse_blaster = SpbiclPulseBlaster()

dev0 = SequenceDevice(0,"device 0",10e-9)
dev1 = SequenceDevice(1,"device 1")#,10e-9)
dev2 = SequenceDevice(2,"device 2",10e-9)

seq = Sequence()
# seq.add_step([],100,seconds.ns)
seq.add_step([dev0,dev2],100,seconds.ns)
seq.add_step([dev0,dev1],100,seconds.ns)
seq.add_step([dev0,dev2],100,seconds.ns)

print(seq_list := pulse_blaster.generate_sequence(seq))
print(set(seq_list))

