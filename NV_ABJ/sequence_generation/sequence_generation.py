__all__ = ["SequenceDevice","SequenceSubset","Sequence"]

from dataclasses import dataclass
from NV_ABJ import seconds

@dataclass
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


class SequenceSubset:
    
    def __init__(self,steps:list=None,loop_steps=0):
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
    


class Sequence:

    def __init__(self,sequence_subsets:list=None):
        if sequence_subsets == None: 
            self.sequence_subsets = []
        else:
            self.sequence_subsets = sequence_subsets
            
    def add_step(self,devices:list=None,duration:float=None, time_unit:seconds=seconds.s):
        sub_sequence = SequenceSubset()
        sub_sequence.add_step(devices,duration,time_unit)
        self.sequence_subsets.append(sub_sequence)
    
    def add_sub_sequence(self, sub_sequence:SequenceSubset):
        self.sequence_subsets.append(sub_sequence)

    def __repr__(self):
        response = ""
        for subset in self.sequence_subsets:
            subs = repr(subset)
            response = response + subs
        return response


dev1 = SequenceDevice(0,"device 1", delayed_to_on_s=100*seconds.ns.value)
dev2 = SequenceDevice(1, "device 2", delayed_to_on_s=300*seconds.ns.value)
dev3 = SequenceDevice(2, "device 3")

# sub = SequenceSubset()
# sub.add_step([dev1,dev2,dev3],1, seconds.ns)
# sub.add_step([dev2,dev3],20e-9)
# sub.add_step([dev1,dev3],30e-9)
# sub.loop_steps = 10
# print(sub)

seq = Sequence()
seq.add_step([dev1,dev2,dev3],10, time_unit = seconds.ns)
seq.add_step([dev1,dev3],20, time_unit = seconds.ns)
seq.add_step([dev1,dev2],30, time_unit = seconds.ns)

# seq.add_sub_sequence(sub)
print(seq)

linear_time_devices = {} # A list of the devices broken into linear time 
time_ns = 0 # Keeping track of the nominal time 

device_states = {} # Keeping track of if devices are on(True) or off(False)

# Opens each subset
for subset in seq.sequence_subsets:
    # Iterates over the loop repeatably 
    for loop_iteration in range(subset.loop_steps+1):
        # Goes through each step 
        for step in subset.steps:
            # Goes through all devices 
            devices_in_step = []
            for dev in step["devices"]:
                # Adjusting the time that the device may be turned on during 
                device_on_ns = time_ns - dev.delayed_to_on_s/seconds.ns.value

                # Appending devices that are in a step to keep track of what devices are on 
                devices_in_step.append(device_states)

                if dev.address in linear_time_devices.keys():
                    # If the device is off we want to turn it on 
                    if not device_states[dev.address]:
                        linear_time_devices[dev.address]["time_turn_on_ns"].append(device_on_ns)
                        device_states[dev.address] = True 
                    # If the device is on and continues to be on we can ignore that case
                else:
                    # The first instance of a device being turned on create the dictionary 
                    linear_time_devices[dev.address] = {"device":dev, "time_turn_on_ns":[device_on_ns], "time_turn_off_ns":[]}
                    device_states[dev.address] = True # Sets device to be known on 
            
            # Turning off all devices that were not in the step
            for dev_address in device_states:
                if dev_address not in devices_in_step:
                    device_states[dev_address] = False
                    linear_time_devices[dev.address]["time_turn_off_ns"].append(time_ns)
            # Adjusting the time taken 
            time_ns = time_ns + step["duration"]*step["time_unit"].value/seconds.ns.value

print(linear_time_devices)

import matplotlib.pyplot as plt
offset_between_devices = 2

for device_number, device_address in enumerate(linear_time_devices.keys()):
    offset = offset_between_devices*device_number
    time_and_signal = []
    for times_on in linear_time_devices[device_address]["time_turn_on_ns"]:
        time_and_signal.append((times_on,offset+1))
    for times_off in linear_time_devices[device_address]["time_turn_off_ns"]:
        time_and_signal.append((times_off,offset))

    plt.plot(time_and_signal,label=linear_time_devices[device_address]["device"].device_label)

plt.legend()
plt.show()    


                
                    

                

