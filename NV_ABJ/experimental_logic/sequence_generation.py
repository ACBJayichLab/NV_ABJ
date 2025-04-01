__all__ = ["SequenceDevice","SequenceSubset","Sequence"]

from dataclasses import dataclass
from NV_ABJ import seconds

@dataclass(unsafe_hash=True)
class SequenceDevice:
    """This is the class that determines the basic properties of a devices passed to a sequence 

    Args:
        address(any): This is an identifier that the pulse generator will use. It could just be an integer 
        device_label(str): This is the general name the device will have e.g. "Green AOM" this name is used for graphs and labels 
        delayed_to_on_s(float): This is how long of a delay from signalling the device to be on to the device actually turning on will be in seconds. Defaults to None
        device_status(bool): This indicates if the device should be turned on when updated True(on) or False(off). Defaults to False (off)
    """
    address:any # What the device that is feed into the sequence class will use to identify the device 
    device_label:str # The name that will be used for labeling and graphing
    delayed_to_on_s:float = 0 # How many seconds it takes to turn on 
    device_status:bool = False # False indicates an off device when updating the devices True will be on

    # This allows us to sort the devices based on the delay time 
    def __lt__(self,other):
        return self.delayed_to_on_s < other.delayed_to_on_s


class SequenceSubset:
    
    def __init__(self,steps:list=None,loop_steps=0,devices:set = None):
        """This subset allows for a sequence to contain loops if you have a repeating sequence inside the overall sequence
        that is a subset and can be made with this class. This would be like an XY8 sequence 

        Args:
            steps (list, optional): The steps that could be added follow a list of a dictionary item in the format [{"devices":[device 1,2,...],"duration":duration, "time_unit":seconds.s},...]. Defaults to None.
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
        step = {"devices":devices, "duration":duration, "time_unit":time_unit}
        self.steps.append(step)
        for device in devices:
            self._devices.add(device)
    


class Sequence:

    def __init__(self,sequence_subsets:list=None,devices:set = None):
        if sequence_subsets == None: 
            self.sequence_subsets = []
        else:
            self.sequence_subsets = sequence_subsets
        if devices == None:
            self._devices = set()
        else:
            self._devices = devices
            
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
    
    def linear_time_sequence(self)-> tuple[dict,set]:
        """This function generates a linear time progression of the sequences and raises errors if a sequence is not possible due to timing of the 
        delays on a device interacting with times it was previously on

        Raises:
            ValueError: if there is a time where a device is off for less than it's delay to on it will raise an error 

        Returns:
            tuple[dict,set]: returns a dictionary containing the devices and times each device is on and a set of all the state changes for a device 
        """
        # seq.add_sub_sequence(sub)
        time_ns = 0 # Keeping track of the nominal time 
        step_times_ns = set() # Set of all unique times 

        devices_currently_on = set() # Keeping track of if devices are on(True) or off(False)
        linear_time_devices = {} # A list of the devices broken into linear time 

        # Creating a dictionary item for each device
        for device in self._devices:
            linear_time_devices[device.address] = {"device":device, "on_times_ns":set()}

        # Opens each subset
        for subset in self.sequence_subsets:
            # Iterates over the loop repeatably 
            for loop_iteration in range(subset.loop_steps+1):
                # Goes through each step 
                for step in subset.steps:

                    # Goes through all devices 
                    devices_on = step["devices"]
                    devices_off = self._devices - set(step["devices"])

                    # Removing any devices that are no longer in the on state
                    devices_currently_on = devices_currently_on-devices_off

                    # Going down in delay time for devices that were off but are now on the last element is then all devices are on
                    delays_decreasing = sorted(list(set(devices_on)-devices_currently_on), reverse=True)

                    if delays_decreasing != []:
                        for dev in delays_decreasing[:-1]:
                            # If the device was off and has a delay we can account for it here 
                            device_on_ns = int(time_ns - dev.delayed_to_on_s/seconds.ns.value)

                            # Confirming there is no time where you have to trigger while it was on but requires a gap
                            if len(list(linear_time_devices[dev.address]["on_times_ns"])) != 0:
                                if max(linear_time_devices[dev.address]["on_times_ns"]) > device_on_ns:
                                    raise ValueError(f"The device is turned off for less time then the delayed time {dev}")
                                
                            # Adjusting the time that the device may be turned on during 
                            step_times_ns.add(device_on_ns) # Adding to the set incase there is a unique time 
                            # Adds the needed start time for the device to be on if it takes time to turn on
                            linear_time_devices[dev.address]["on_times_ns"].add(device_on_ns) 

                        
                        # Using the time for the last delay that had to be turned on for all devices on
                        device_on_ns = int(time_ns - delays_decreasing[-1].delayed_to_on_s/seconds.ns.value)
                        for dev in devices_on:
                            linear_time_devices[dev.address]["on_times_ns"].add(device_on_ns)
                            # Adds the device to those that are on 
                            devices_currently_on.add(dev)
                            step_times_ns.add(device_on_ns) # Adding to the set incase there is a unique time 

                            # Confirming there is no time where you have to trigger while it was on but requires a gap
                            if len(list(linear_time_devices[dev.address]["on_times_ns"])) != 0:
                                if max(linear_time_devices[dev.address]["on_times_ns"]) > device_on_ns:
                                    raise ValueError(f"The device is turned off for less time then the delayed time {dev}")

                    else:
                        for dev in devices_on:
                            linear_time_devices[dev.address]["on_times_ns"].add(time_ns)
                            devices_currently_on.add(dev)
                            step_times_ns.add(time_ns) # Adding to the set incase there is a unique time 

                    if devices_off == self._devices:
                        step_times_ns.add(time_ns) # Adding to the set incase there is a unique time 

                    # Skipping durations that are 0 in length
                    if step["duration"] != None and step["duration"] != 0:
                        # Increasing time by one step in the sequence 
                        time_ns = int(time_ns+step["duration"]*step["time_unit"].value/seconds.ns.value)

        # Adding the ending time and converting set to a sorted list
        step_times_ns.add(time_ns) 
        step_times_ns = list(step_times_ns)
        step_times_ns.sort()

        return linear_time_devices, step_times_ns