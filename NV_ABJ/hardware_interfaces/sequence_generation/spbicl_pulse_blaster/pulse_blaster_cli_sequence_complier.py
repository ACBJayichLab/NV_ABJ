import subprocess
from tempfile import TemporaryDirectory
from os.path import join

from NV_ABJ.abstract_device_interfaces.pulse_generator import PulseGenerator
from NV_ABJ.sequence_generation.sequence_generation import *
from NV_ABJ.units import seconds

def generate_sequence(sequence_class:Sequence)->str:
        """This function takes the sequence class and converts it into a format that can be interpreted by the pulse blaster 

        Args:
            sequence_class (Sequence): A sequence of the devices and times you wish to add

        Returns:
            str: This returns a string that can be used to load the sequence into the pulse blaster 
            This command is going to commonly be followed by load(sequence) they are kept separate because load 
            is a more general function and you may want to generate sequences and save them without 
        """
        available_ports = 23
        maximum_step_time_s = 5

        def generate_line(binary_address:int,operator=111)->str:
            """generates the bit formulation
            Args:
                binary_address (int): address line
            Returns:
                str: The line made from address and duration
            """

            # Generate the bit line
            address_line = str(operator)+str(binary_address).zfill(available_ports-2)
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
                print(final_time_on)

                # Finding the devices that were on in the end 
                devices_on_in_end = set()
                for device_address in linear_time_devices:
                    if final_time_on == max(linear_time_devices[device_address]["on_times_ns"]):
                        devices_on_in_end.add(device_address)
                print(devices_on_in_end)

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

                print("Shifts")
                print(devices_needing_shift)
                print(shifted_times)

                # For devices that need to be shifted we need to recursively add them in descending order
                if shifted_times != []:
                    sorted_shift = zip(*sorted(zip(shifted_times, devices_needing_shift), reverse=False))
                    
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

                # Finding devices that are on during this time 
                for device in sequence_class._devices:
                    if step_time in linear_time_devices[device.address]["on_times_ns"]:
                            addresses = addresses + pow(10,device.address)
                
                # Finds the duration by simple subtraction 
                duration_ns = int(step_times_ns[ind+1]-step_time)
                
                # If the duration is longer than the maximum time for a single step it loops adding steps and subtracting the duration 
                while duration_ns > maximum_step_time_s/seconds.ns.value:
                    duration_ns = int(duration_ns - maximum_step_time_s/seconds.ns.value)
                    # Adding 1 to sequence length so we don't have issues when a value is maxed out on time and is the end of the sequence
                    sequence_list.append((addresses,int(maximum_step_time_s/seconds.ns.value)))
            
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

            sequence_text = f"start: 0b{generate_line(addresses)}, {int(maximum_step_time_s/seconds.ns.value)} ns, branch, start"
            return sequence_text
        
        # If there are zero lines in the sequence
        else:
            raise ValueError("Sequence must contain one or more steps")


dev0 = SequenceDevice(0,"device 0",10e-9)
dev1 = SequenceDevice(1,"device 1")#,10e-9)
dev2 = SequenceDevice(2,"device 2",10e-9)

seq = Sequence()
# seq.add_step([],100,seconds.ns)
seq.add_step([dev0,dev2],100,seconds.ns)
seq.add_step([dev0,dev1],101,seconds.ns)
seq.add_step([dev0,dev2],102,seconds.ns)
linear_time, times = seq.linear_time_sequence()
for device_address in linear_time:
    print(device_address)
    print(linear_time[device_address]["on_times_ns"])

# print(seq_list := generate_sequence(seq))
# print(set(seq_list))

