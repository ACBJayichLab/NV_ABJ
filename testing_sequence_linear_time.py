__all__ = ["SequenceDevice","SequenceSubset","Sequence"]

from dataclasses import dataclass
from NV_ABJ import seconds
import numpy as np

@dataclass(unsafe_hash=True)
class SequenceDevice:
    """This is the class that determines the basic properties of a devices passed to a sequence 

    Args:
        address(any): This is an identifier that the pulse generator will use. It could just be an integer 
        device_label(str): This is the general name the device will have e.g. "Green AOM" this name is used for graphs and labels 
        delayed_to_on_s(float): This is how long of a delay from signalling the device to be on to the device actually turning on will be in seconds. Defaults to 0
        device_status(bool): This indicates if the device should be turned on when updated True(on) or False(off). Defaults to False (off)
    """
    address:any # What the device that is feed into the sequence class will use to identify the device 
    device_label:str # The name that will be used for labeling and graphing
    delayed_to_on_s:float = 0 # How many seconds it takes to turn on must be greater than or equal to zero
    device_status:bool = False # False indicates an off device when updating the devices True will be on

    # This allows us to sort the devices based on the delay time 
    def __lt__(self,other):
        return self.delayed_to_on_s < other.delayed_to_on_s


class SequenceSubset:
    
    def __init__(self,steps:list=None,loop_steps=0,devices:set = None):
        """This subset allows for a sequence to contain loops if you have a repeating sequence inside the overall sequence
        that is a subset and can be made with this class. This would be like an XY8 sequence 

        Args:
            steps (list, optional): The steps that could be added follow a list of a dictionary item in the format [{"devices":set(device 1,2,...),"duration":duration, "time_unit":seconds.s},...]. Defaults to None.
            loop_steps (int, optional): How many times this sub sequence will be looped. Defaults to 0.
        """
        if steps == None:
            self.steps = []
        else:
            self.steps = steps
        self.loop_steps = loop_steps # when set to zero it wont be looped

        if devices == None:
            self._devices = set()
        else:
            self._devices = devices

    def __repr__(self):
        response = f"Following is looped {self.loop_steps} times\n"
        for item in self.steps:
            devices = []
            if item["devices"] != None:
                for dev in item["devices"]:
                    devices.append(dev.device_label)

            response = response + f"    devices on:{devices}, duration of step: {item["duration"]} {item["time_unit"].name}\n"

        return str(response)
    
    def add_step(self,devices:list=None,duration:float=None,time_unit:seconds=seconds.s):
        """Adds a step to the sub sequence 

        Args:
            devices (list, optional): List of devices to turn on. If none are given it is assumed no devices are on. Defaults to None.
            duration (float, optional): How long the step will last. If none are given it will be removed when a sequence is generated. Defaults to None.
            time_units (seconds, optional): Defaults to seconds but you can enter any item from the seconds enum [ps, ns, us, ms, cs, ds, s, das, hs, ks, Ms, Gs, Ts]. Defaults to seconds.s
        """
        step = {"devices":set(devices), "duration":duration, "time_unit":time_unit}
        self.steps.append(step)
        for device in devices:
            self._devices.add(device)
    


class Sequence:

    def __init__(self,sequence_subsets:list=None,devices:set = None,loop_end_condition:bool=True):
        if sequence_subsets == None: 
            self.sequence_subsets = []
        else:
            self.sequence_subsets = sequence_subsets
        if devices == None:
            self._devices = set()
        else:
            self._devices = devices
        self.loop_end_condition = loop_end_condition
            
    def add_step(self,devices:list=None,duration:float=None, time_unit:seconds=seconds.s):
        sub_sequence = SequenceSubset()
        sub_sequence.add_step(devices,duration,time_unit)
        self.sequence_subsets.append(sub_sequence)
        self._devices.update(sub_sequence._devices)
    
    def add_sub_sequence(self, sub_sequence:SequenceSubset):
        self.sequence_subsets.append(sub_sequence)
        self._devices.update(sub_sequence._devices)

    def __repr__(self):
        response = ""
        for subset in self.sequence_subsets:
            subs = repr(subset)
            response = response + subs
        return response
    
    def linear_time_sequence(self,wrapped:bool=True, remove_none_addresses:bool=True)-> tuple[dict,set]:
        """This function generates a linear time progression of the sequences and raises errors if a sequence is not possible due to timing of the 
        delays on a device interacting with times it was previously on

        Raises:
            ValueError: if there is a time where a device is off for less than it's delay to on it will raise an error 

        Returns:
            tuple[dict,set]: returns a dictionary containing the devices and times each device is on and a set of all the state changes for a device 
        """

        # Finding the time without delays added on 
        time_ns = 0 # Keeping track of the nominal time 
        step_times_ns = set() # Set of all unique times 

        devices_previously_on = set() # Keeping track of if devices are on(True) or off(False)
        linear_time_devices = {} # A list of the devices broken into linear time 

        # Creating a dictionary item for each device
        for device in self._devices:
            if remove_none_addresses:
                if device.address != None:
                    linear_time_devices[device.address] = {"device":device, "on_times_ns":set()}
            else:
                linear_time_devices[device.address] = {"device":device, "on_times_ns":set()}



        # Opens each subset
        for subset in self.sequence_subsets:
            # Iterates over the loop repeatably 
            for loop_iteration in range(subset.loop_steps+1):
                # Goes through each step 
                for step in subset.steps:
                    
                    # Skipping durations that are 0 in length
                    if step["duration"] != None and step["duration"] != 0:
                        # Goes through all devices 
                        devices_on = step["devices"]
                        devices_off = self._devices - set(step["devices"])

                        # Removing None addresses if asked
                        if remove_none_addresses:
                            # temporary variables to remove it so the set size doesn't change on iteration
                            devices_on_temp = devices_on.copy()
                            devices_off_temp = devices_off.copy()

                            # Removing from on devices 
                            for dev in devices_on:
                                if dev.address == None:
                                    devices_on_temp.remove(dev)
                            
                            # Removing from off devices 
                            for dev in devices_off:
                                if dev.address == None:
                                    devices_off_temp.remove(dev)
                            
                            devices_on = devices_on_temp
                            devices_off = devices_off_temp
                            
                            # Clearing up space 
                            del devices_off_temp, devices_on_temp

                        # Adding the time that the device is on for and the delay times 
                        delay_times = set()
                        for dev in sorted(devices_on):
                            # Adding the time it needs to be on 
                            linear_time_devices[dev.address]["on_times_ns"].add(time_ns)

                            delay_times.add(np.round(dev.delayed_to_on_s/seconds.ns.value))

                            # We need to add the delay for each device where the longest delay is last  
                            # and every delay gains the time the previous device was on for as well 
                            for delay in delay_times:
                                # Adding the time for the on delay 
                                delayed_time = np.round(time_ns-delay)
                                linear_time_devices[dev.address]["on_times_ns"].add(delayed_time)
                                step_times_ns.add(delayed_time)

                                # We also need to add this time for devices that were previously on
                                for dev_prev in devices_previously_on:
                                    linear_time_devices[dev_prev.address]["on_times_ns"].add(delayed_time)


                        devices_previously_on = devices_on

                        # Increasing time by one step in the sequence 
                        time_ns = np.round(time_ns+step["duration"]*step["time_unit"].value/seconds.ns.value)
                        # Adding the time to the set as long as there is a duration
                        step_times_ns.add(time_ns) 
        
        final_time_ns = time_ns
        # We want to add the final time to the devices on so it doesn't appear that they turn off at the end of the sequence 
        for device in devices_on:
            linear_time_devices[device.address]["on_times_ns"].add(final_time_ns)
        
        # Adding the ending time and converting set to a sorted list
        step_times_ns.add(final_time_ns) 
        step_times_ns = list(step_times_ns)
        step_times_ns.sort()

        # If we are wrapping the text this is where we check if the bits that are on are on in the end time this is a time shift 
        # from the maximum time to the end time 
        if wrapped:
            # Getting the devices that need to be wrapped
            devices_needing_wrap = []
            shifting_times = []
            for device_address in linear_time_devices:
                if (shift_time := min(linear_time_devices[device_address]["on_times_ns"])) < 0:   
                    devices_needing_wrap.append(linear_time_devices[device_address]["device"])
                    shifting_times.append(final_time_ns + shift_time)

            if shifting_times != []:
                # We need to iterate from the longest delay 
                shifting_times,devices_needing_wrap = zip(*sorted(zip(shifting_times,devices_needing_wrap)))
                

                # We now need to add the times to every device that is on within the delay of being turned on
                #  this way we don't turn off any digits accidentally 
                for shift_time in shifting_times:
                    for ind,time in enumerate(step_times_ns[:-1]):
                        next_time = step_times_ns[ind+1]
                        # Checking if the shifted time is between the time on and off 
                        if shift_time < next_time and shift_time > time:
                            # If a device is on and the shifted time falls between the next step in time 
                            # we want to add that time to the device as well 
                            for device_address in linear_time_devices:
                                if time in (times_on := linear_time_devices[device_address]["on_times_ns"]):
                                    if next_time in times_on:
                                        times_on.add(shift_time)

                # Adding the shift time to devices that are shifted but not on 
                for device in devices_needing_wrap:
                    linear_time_devices[device.address]["on_times_ns"] = linear_time_devices[device.address]["on_times_ns"] | set(shifting_times)
                    linear_time_devices[device.address]["on_times_ns"].add(final_time_ns)

                stp_tm = set(step_times_ns) 

                # Removing zeros from times 
                for step_time in step_times_ns:
                    if step_time < 0:
                        stp_tm.remove(step_time)

                        for device_address in linear_time_devices:
                            if step_time in (times_on := linear_time_devices[device_address]["on_times_ns"]):
                                times_on.remove(step_time)
                        
                # Adding shift times to overall times 
                step_times_ns = stp_tm | set(shifting_times) | set([0])
                step_times_ns = list(step_times_ns)
                step_times_ns.sort()


            # We now have a list of times and devices on but there are going to be multiple times that are unnecessary because 
            # the state for the devices does not change we want to remove any times where the state does not change 
            
            # We can't change the set size while iterating so we have to use temporary variables and we can remove 
            # The unnecessary times from there 
            lin_time_dict = linear_time_devices.copy()
            stp_tm = step_times_ns.copy()

            # getting the devices that are on at this step 
            devices_previously_on = set()
            devices_currently_on = set()
            times_to_remove = set()

            for index,step_time in enumerate(step_times_ns[:-1]): 
                # Getting the previous time 
                previous_time = step_times_ns[index]

                devices_previously_on.clear()
                devices_currently_on.clear()
                times_to_remove.clear()



                # Getting which devices were on before and now
                for device_address in lin_time_dict:               
                    if previous_time in lin_time_dict[device_address]["on_times_ns"]:
                        devices_previously_on.add(device_address)

                # If the devices were equal we want to find all the time it takes until they are no longer equal
                for ind,s_t in enumerate(step_times_ns[index+1:]): 
                    devices_currently_on.clear()

                    # Getting which devices were on before and now
                    for device_address in lin_time_dict:
                        if s_t in lin_time_dict[device_address]["on_times_ns"]:
                            devices_currently_on.add(device_address)

                    if devices_currently_on == devices_previously_on:
                        times_to_remove.add(s_t)
                            
                    if devices_currently_on != devices_previously_on or s_t == final_time_ns: 
                        for t in times_to_remove:
                            if t in stp_tm and t != final_time_ns:
                                stp_tm.remove(t)
                            for device_address in devices_previously_on:
                                if t in (lin := lin_time_dict[device_address]["on_times_ns"]):
                                    lin.remove(t)               
                        break

        stp_tm = set(stp_tm)
        stp_tm.add(0)
        step_times_ns = list(stp_tm)
        step_times_ns.sort()

        return lin_time_dict, step_times_ns
    
    def create_instructions(self,allow_only_looping:bool = False, allow_looping_and_subroutine:bool = True,wrapped:bool=True,remove_none_addresses:bool=True):
        # We want to start with what the linear time has already given us time wise
        linear_time_dict, step_times = self.linear_time_sequence(wrapped=wrapped,remove_none_addresses=remove_none_addresses)
        
        # print(step_times)
        # for device_address in linear_time_dict:
        #     print(device_address)
        #     print(linear_time_dict[device_address]["on_times_ns"])
        instruction_set = {}
        
        # We want to convert into a list of instructions 
        for ind,time in enumerate(step_times[:-1]):
            instruction_set[ind] = {}
            instruction_set[ind]["duration"] = step_times[ind+1]-time
            instruction_set[ind]["devices"] = set()

            for device_address in linear_time_dict:
                if time in linear_time_dict[device_address]["on_times_ns"]:
                    instruction_set[ind]["devices"].add(device_address)



        if allow_looping_and_subroutine:
            pass
        elif allow_only_looping:
            pass

        return instruction_set


dev0 = SequenceDevice(0,"device 0",10e-9)
dev1 = SequenceDevice(1,"device 1",20e-9)
dev2 = SequenceDevice(2,"device 2",30e-9)

sub = SequenceSubset()
sub.add_step([dev0,dev2],100,seconds.ns)
sub.add_step([dev0,dev1],100,seconds.ns)
sub.loop_steps = 10

seq = Sequence()
seq.add_step([],100,seconds.ns)
seq.add_sub_sequence(sub)
seq.add_step([dev0,dev2],100,seconds.ns)
seq.add_step([dev0,dev1],100,seconds.ns)
seq.add_step([dev0,dev2],200,seconds.ns)
seq.add_step([],100,seconds.ns)

instructions = seq.create_instructions()

for instruction in instructions:
    print(instructions[instruction])
