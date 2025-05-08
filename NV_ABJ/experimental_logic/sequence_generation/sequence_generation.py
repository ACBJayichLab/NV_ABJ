__all__ = ["SequenceDevice","SequenceSubset","Sequence","SequenceDeviceConfiguration"]

from dataclasses import dataclass
import copy

@dataclass(frozen=True)
class SequenceDeviceConfiguration:
    """This is a immutable subclass to the sequence device class this is how we want to configure the devices within.
    These are things that should not change for the device during the course of the experiment 
    """
    address:int # What the device that is feed into the sequence class will use to identify the device 
    delayed_to_on_ns:int = 0 # How many nano-seconds it takes to turn on must be greater than or equal to zero
    inverted_output:bool = False # If the output needs to be inverted to function. Inverted means when pulse blaster powers pin the device turns off

    def __lt__(self,other):
        return self.delayed_to_on_ns < other.delayed_to_on_ns

class SequenceDevice:
    def __init__(self,address:int,delayed_to_on_ns:int=0,inverted_output:bool=False,
                 device_status:bool = False, device_label:str = None, graph_order = None, graph_color = None):

        if delayed_to_on_ns >= 0 and type(address) == int and type(inverted_output) == bool:
            self.config:SequenceDeviceConfiguration = SequenceDeviceConfiguration(address=address,delayed_to_on_ns=delayed_to_on_ns,inverted_output=inverted_output)
        else:
            raise ValueError("The assignment of the address, delayed on, or inverted output was not correct")
        
        self.device_status:bool = device_status # False indicates an off device when updating the devices True will be on
        self.device_label:str = device_label # The name that will be used for labeling and graphing
        
        self.graph_color:str = graph_color # color that it will be graphed as
        self.graph_order:int = graph_order # The order which items will be graphed, higher numbers are higher up on the y axis 

class SequenceSubset:
    
    def __init__(self,loop_steps:int=0):
        """This subset allows for a sequence to contain loops if you have a repeating sequence inside the overall sequence
        that is a subset and can be made with this class. This would be like an XY8 sequence 

        Args:
            loop_steps (int, optional):  How many times this sub sequence will be looped. Defaults to 0.
        """

        self.steps = []
        self.loop_steps = loop_steps # when set to zero it wont be looped
        self.devices = set()

    def add_step(self,duration_ns:float=0,devices:list=[]):
        """Adds a step to the sub sequence 

        Args:
            devices (list, optional): List of devices to turn on. If none are given it is assumed no devices are on. Defaults to None.
            duration_ns (float, optional): How long the step will last. If none are given it will be removed when a sequence is generated. Defaults to None.
        """

        if duration_ns > 0:
            device_set = set()
            for device in devices:

                # This is creating a set of all devices without the address None. If the address is none then it will ignore the device
                # This is so we can have the same sequence for setups that may not require a device but we still want to have transferability
                if device.config.address != None:
                    device_set.add(device.config)
                
            step = (duration_ns,device_set)
            self.steps.append(step)
            # Adding the devices for this step to all devices used 
            self.devices = self.devices | set(device_set)
        elif duration_ns == 0:
            pass
        else:
            raise ValueError(f"You can not enter a duration less than 0 you entered {duration_ns}")
        
    def __repr__(self):

        steps_text = ""
        for step in self.steps:
            steps_text = steps_text + "\t" + str(step) + "\n"

        return f"\n Steps:{steps_text}\nDevice:{self.devices}\nLooped:{self.loop_steps}"
    


class Sequence:
    def __init__(self):
        self.steps = []
        self.devices = set()
            
    def add_step(self,duration_ns:float=0,devices:list=[]):
        """Adds a singular step to the sequence by calling a sub sequence to make the step

        Args:
            devices (list, optional): The devices we want to add. Defaults to [] which will be ignored 
            duration_ns (float, optional): The duration in ns we want to add. Defaults to 0 which will ignore the step 
        """
        sub_sequence = SequenceSubset()
        # Passing to the sub sequence because we want all steps generated the same
        sub_sequence.add_step(devices=devices,duration_ns=duration_ns)
        self.add_sub_sequence(sub_sequence=sub_sequence)
    
    def add_sub_sequence(self, sub_sequence:SequenceSubset):
        """Allows you to add a subsequence to the sequence. This will unwrap the sequence into the sequence steps 

        Args:
            sub_sequence (SequenceSubset): The subsequence you have created
        """
        # This prevents issues that can arise from feeding the sequence itself 
        sub_sequence = copy.deepcopy(sub_sequence)

        if type(sub_sequence) == SequenceSubset:
            # Loops through the sub sequence for the amount of times it was specified 
            looping_times = sub_sequence.loop_steps+1
            for i in range(looping_times):
                for step in sub_sequence.steps:
                    self.steps.append(step)
            
            self.devices.update(sub_sequence.devices)
        
        elif type(sub_sequence) == Sequence:
            for step in sub_sequence.steps:
                self.steps.append(step)
            self.devices.update(sub_sequence.devices)
        
        else:
            raise ValueError(f"You must input a Sequence class or a SequenceSubset class to add you entered a:{type(sub_sequence)}")
        

    def __repr__(self):
        steps_text = ""
        for step in self.steps:
            steps_text = steps_text + "\t" + str(step) +"\n"
        return f"\nSteps:\n{steps_text}\nDevice:{self.devices}"
    

    def linear_time_sequence(self,wrapped:bool=True)-> tuple[dict,set]:
        """This function generates a linear time progression of the sequences and raises errors if a sequence is not possible due to timing of the 
        delays on a device interacting with times it was previously on. It also applies the delay for the devices 

        Raises:
            ValueError: if there is a time where a device is off for less than it's delay to on it will raise an error 

        Returns:
            tuple[dict,set]: returns a dictionary containing the devices and times each device is on and a set of all the state changes for a device 
        """

        # Finding the time without delays added on 
        time_ns = 0 # Keeping track of the nominal time 
        step_times_ns = set([0]) # Set of all unique times 

        sequence_devices = {} # A list of the devices broken into linear time 
        devices_with_delays = set() # A list of all devices that have delays 

        for device in self.devices:
            sequence_devices[device.address] = {"device":device,"on_times_ns":set()}
            
            if device.delayed_to_on_ns > 0:
                devices_with_delays.add(device)


        temp_steps = self.steps

        # Adding in the first step
        previous_duration = temp_steps[0][0]
        devices_previously_on = temp_steps[0][1]
        devices_on_before_start = set()
        
        devices_previously_on_sorted = sorted(devices_previously_on)
        for ind,device in enumerate(devices_previously_on_sorted):
            for dev in devices_previously_on_sorted[ind:]:
                sequence_devices[dev.address]['on_times_ns'].add(-device.delayed_to_on_ns)
                sequence_devices[dev.address]['on_times_ns'].add(time_ns)
            
            if device.delayed_to_on_ns > 0:
                # Getting the devices that will need to be wrapped
                devices_on_before_start.add(device)

            step_times_ns.add(-device.delayed_to_on_ns)

        time_ns = time_ns + previous_duration
        step_times_ns.add(time_ns)


        # Adds the times the device is already on from the list 
        for ind,step in enumerate(temp_steps[1:]):
            duration = step[0] 
            devices = step[1]

            # If there are devices in the step
            if devices != set():
                devices_with_delays_new = devices_with_delays.intersection(devices - devices_previously_on)
                # If the previous devices are the same as the ones that are now on we don't want to account for any delays 
                if devices_with_delays_new == set():
                    for device in devices:
                        sequence_devices[device.address]["on_times_ns"].add(time_ns)
                        step_times_ns.add(time_ns)
                        

                # If there is a device with a delay in it we want to account for it 
                else:
                    # If the devices are on during the time we want to add the time when this device turns on 
                    devices_with_delays_new_sorted = sorted(devices_with_delays_new)
                    for device in devices_with_delays_new_sorted:

                        device_time = time_ns-device.delayed_to_on_ns

                        # Checks if the delay time is overlapping with when it was previously on
                        if len(sequence_devices[device.address]["on_times_ns"]) > 0 and max(sequence_devices[device.address]["on_times_ns"]) > device_time:
                            raise ValueError(f"The devices delayed on overlaps with when it was previously on the duration.\nDevice:{sequence_devices[device.address]["device"]}\nStep:{step}\nIndex:{ind}")

                        sequence_devices[device.address]["on_times_ns"].add(device_time)
                        step_times_ns.add(device_time)

                        for device_previous in devices_previously_on:
                            sequence_devices[device_previous.address]["on_times_ns"].add(device_time)
                    
                    # We now need to add the devices that don't have a delay to the timeline 
                    new_devices_on_without_delays = devices-devices_previously_on-devices_with_delays_new
                    
                    for device in new_devices_on_without_delays:
                        sequence_devices[device.address]["on_times_ns"].add(time_ns)
                        step_times_ns.add(time_ns)

                        # We want to add the time to all devices that continue to be on for this step 
                        for device_on in devices:
                            sequence_devices[device_on.address]["on_times_ns"].add(time_ns)
            
            # Without devices in the step we still need to add the time to step so the devices that were on before will have an indication to turn off
            else:
                step_times_ns.add(time_ns)


            # Updating which devices were previously on
            devices_previously_on = devices
            time_ns = time_ns + duration

        # Adding the final time_ns
        step_times_ns.add(time_ns)

        # for wrapping 
        devices_on_in_end = devices_previously_on

        if wrapped:
            # We need devices that were on at the very start
            
            # This removes any devices that are on before the start but are already on in the end 
            devices_needing_shifting = devices_on_before_start-devices_on_in_end

            devices_needing_shifting_sorted = sorted(devices_needing_shifting)

            for shifted_device in devices_needing_shifting_sorted:
                
                # Find what devices are on in the duration between the shift and the end 
                shifted_time = time_ns + min(sequence_devices[shifted_device.address]["on_times_ns"])

                sequence_devices[shifted_device.address]["on_times_ns"].add(shifted_time)
                step_times_ns.add(shifted_time)

                step_times_ns_sorted = sorted(step_times_ns)

                for ind, time in enumerate(step_times_ns_sorted[:-1]):
                    future_time = step_times_ns_sorted[ind+1]

                    if time <= shifted_time and shifted_time < future_time:

                        for device_address in sequence_devices:
                            times = sequence_devices[device_address]["on_times_ns"]

                            if time in times:
                                sequence_devices[device_address]["on_times_ns"].add(shifted_time)
                            

            # When all devices are wrapped around we can remove the negative values from all lists 
            for device_address in sequence_devices:
                times = sequence_devices[device_address]["on_times_ns"]
                temp = times.copy()
                for time in times:
                    if time < 0:
                        temp.remove(time)
                sequence_devices[device_address]["on_times_ns"] = temp
            
            temp = step_times_ns.copy()
            for time in step_times_ns:
                if time < 0:
                    temp.remove(time)
            step_times_ns = temp


        # Finding any inverted output devices
        inverted_devices = set()
        for device in self.devices:
            if device.inverted_output:
                inverted_devices.add(device)

        # Taking care of any inverted outputs 
        if inverted_devices != set():
            # Because we are inverting bits we want an independent copy of the steps to not affect the sequence 

            for device in inverted_devices:
                # Inverting all the outputs
                on_times_ns = step_times_ns-sequence_devices[device.address]['on_times_ns']
                sequence_devices[device.address]['on_times_ns'] = on_times_ns


        return sequence_devices, sorted(step_times_ns)
    
    def instructions(self,allow_subroutine:bool = True,wrapped:bool=True):
        # We want to start with what the linear time has already given us time wise
        linear_time_dict, step_times = self.linear_time_sequence(wrapped=wrapped)

        instruction_set = []
        
        # We want to convert into a list of instructions 
        for ind,time in enumerate(step_times[:-1]):
            instruction_set.append([step_times[ind+1]-time,set()])

            for device_address in linear_time_dict:
                if time in linear_time_dict[device_address]["on_times_ns"]:
                    instruction_set[ind][1].add(device_address)                   


        if allow_subroutine:

            def finding_maximum_sequence(seq):
                max_len = int(len(seq) / 2)
                for x in range(2, max_len):
                    if str(seq[0:x]) == str(seq[x:2*x]) :
                        return x,seq[0:x]

                return 1, []
    
            # Enters loop
            count = 0
            sub_routines = {}
            reduced_instructions = {}
            reduced_instructions_length = 0
            final_instruction_index = -1

            for i,line in enumerate(instruction_set):
                length, seq = finding_maximum_sequence(instruction_set[i:])

                # If the length is longer than 1 we can loop it 
                if length != 1 and i > final_instruction_index:
                    
                    key = None
                    # We want to check if the sequence is in the sub_routines
                    for sub in sub_routines:
                        if sub_routines[sub] == seq:
                            key = sub
                    if key == None:
                        key = count
                        sub_routines[key] = seq
                        count = count + 1
                    
                    # We now want to find the number of times this list is repeated 
                    instances = 0
                    inst = instruction_set[i:]

                    for ind, _ in enumerate(inst):
                        if str(seq) == str(inst[ind*(length):(ind+1)*(length)]):
                            instances = instances+1

                        else:
                            break
                    
                    final_instruction_index = i+instances*length-1

                    # Adding to the reduced instructions with the number of loops
                    reduced_instructions[reduced_instructions_length] = (True,key,instances)
                    
                    # Incrementing the reduced instruction set by one 
                    reduced_instructions_length = reduced_instructions_length + 1


                elif length == 1 and i > final_instruction_index:
                        # If this is not the start to a loop we want to make sure to add it to the list 
                        reduced_instructions[reduced_instructions_length] = (False,line,0)
                    
                        # Incrementing the reduced instruction set by one 
                        reduced_instructions_length = reduced_instructions_length + 1
            
            instructions = reduced_instructions
        
        else:
            instructions = {}
            sub_routines = {}
            for ind, item in enumerate(instruction_set):
                instructions[ind] = (False,item,0)

        return instructions,sub_routines
    
    def add_devices(self, devices_to_add:list[SequenceDevice]):
        """if you have inverted devices that are not called you should add your devices here"""
        for device in devices_to_add:
            self.devices.add(device.config)    

if __name__ == "__main__":
        
        # from experimental_configuration import *

        import matplotlib.pyplot as plt 
        import numpy as np

        def generate_sequence(depopulation_time_s:float,iq_time_s:float,pi_pulse_duration_s:float,wait_time_s:float,readout_trigger_duration_s:float,readout_time_s:float,green_pulse_duration_s:float,
                          rf_iq_trigger:SequenceDevice,rf_trigger:SequenceDevice,laser_trigger:SequenceDevice,readout_trigger:SequenceDevice) -> Sequence:
        
            """This is a pulsed esr sequence utilizing a signal and a reference later that should be normalized to each other"""
            seq = Sequence()

            # signal
            seq.add_step(green_pulse_duration_s*1e9                       ,[laser_trigger])
            seq.add_step((depopulation_time_s-iq_time_s)*1e9              ,[])
            seq.add_step(iq_time_s*1e9                                    ,[rf_iq_trigger])
            seq.add_step(pi_pulse_duration_s*1e9                          ,[rf_iq_trigger,rf_trigger])
            seq.add_step(iq_time_s*1e9                                    ,[rf_iq_trigger])
            seq.add_step((wait_time_s-iq_time_s)*1e9                      ,[])
            seq.add_step(readout_trigger_duration_s*1e9                   ,[laser_trigger,readout_trigger])
            seq.add_step((readout_time_s-readout_trigger_duration_s)*1e9  ,[laser_trigger])
            seq.add_step((readout_trigger_duration_s)*1e9                 ,[laser_trigger,readout_trigger])


            # reference
            seq.add_step(green_pulse_duration_s*1e9                        ,[laser_trigger])
            seq.add_step(depopulation_time_s*1e9                           ,[])
            seq.add_step(wait_time_s*1e9                                   ,[])
            seq.add_step(readout_trigger_duration_s*1e9                    ,[laser_trigger,readout_trigger])
            seq.add_step((readout_time_s-readout_trigger_duration_s)*1e9   ,[laser_trigger])
            seq.add_step(readout_trigger_duration_s*1e9                    ,[laser_trigger,readout_trigger])

            return seq
                
        rf_1_iq_pos_x_trigger = SequenceDevice(address=2,delayed_to_on_ns=0,inverted_output=False,device_label="RF1 IQ+X")
        rf_1_trigger = SequenceDevice(address=3,delayed_to_on_ns=0,inverted_output=False,device_label="RF1")
        green_aom_trigger = SequenceDevice(address=0,delayed_to_on_ns=0,inverted_output=False,device_label="Green AOM")
        apd_1_trigger = SequenceDevice(address=1,delayed_to_on_ns=0,inverted_output=False,device_label="APD Trigger")

        seq = generate_sequence(depopulation_time_s=200e-9,
                                            iq_time_s=40e-9,
                                            pi_pulse_duration_s=75e-9,
                                            wait_time_s=2000e-9,
                                            readout_trigger_duration_s=50e-9,
                                            readout_time_s=400e-9,
                                            green_pulse_duration_s=2000e-9,
                                            # Device Trigger
                                            rf_iq_trigger=rf_1_iq_pos_x_trigger,
                                            rf_trigger=rf_1_trigger,
                                            laser_trigger=green_aom_trigger,
                                            readout_trigger=apd_1_trigger)
        
        seq.add_sub_sequence(seq)
        inst = seq.instructions()[0]


        fig, ax = plt.subplots()
        time_ns = 0
        offset_amount = 1
        offset_device = {}

        color_options = ['#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']

        devices = {}
        for dev in seq.devices:
            devices[dev.address] = dev

        for inst_ind in inst:
            line = inst[inst_ind][1]
            duration = line[0]
            for device_address in line[1]:
                

                if device_address not in offset_device.keys():
                    offset_device[device_address] = {"blocks_x":[],"blocks_y":[]}

                offset_device[device_address]["blocks_x"].append([time_ns,time_ns,time_ns+duration,time_ns+duration])
                offset_device[device_address]["blocks_y"].append(np.array([0,1,1,0]))

            time_ns = time_ns + duration

        y_ticks = []
        y_tick_names = []



        for ind,device_address in enumerate(sorted(offset_device.keys())):
            color = color_options[device_address]
            offset = ind
            y_ticks.append(ind+.5)
            # y_tick_names.append(devices[device_address].device_label)

            for block_x, block_y in zip(offset_device[device_address]["blocks_x"],offset_device[device_address]["blocks_y"]):
                plt.fill(block_x,block_y+offset, color=color)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_tick_names)
        ax.set_xlabel("Time")
        ax.set_xticklabels([])
        ax.set_xticks([])
        plt.show()
        # inst = seq.steps
        # for line in inst:
        #     print(line) 