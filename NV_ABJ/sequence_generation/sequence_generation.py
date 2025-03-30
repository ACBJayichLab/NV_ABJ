__all__ = ["SequenceDevice","SequenceSubset","Sequence"]

from dataclasses import dataclass

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
    delayed_to_on_s:float = None # How many seconds it takes to turn on 
    device_status:bool = False # False indicates an off device when updating the devices True will be on


class SequenceSubset:
    
    def __init__(self,steps:list=None,loop_steps=0):
        """This subset allows for a sequence to contain loops if you have a repeating sequence inside the overall sequence
        that is a subset and can be made with this class. This would be like an XY8 sequence 

        Args:
            steps (list, optional): The steps that could be added follow a list of a dictionary item in the format [{"devices":[device 1,2,...],"duration_s":duration_s},...]. Defaults to None.
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

            response = response + f"    devices on:{devices}, duration of step: {item["duration_s"]} s\n"

        return str(response)
    
    def add_step(self,devices:list=None,duration_s:float=None):
        """Adds a step to the sub sequence 

        Args:
            devices (list, optional): list of devices to turn on. If none are given it is assumed no devices are on. Defaults to None.
            duration_s (float, optional): how long the step will last in seconds. If none are given it will be removed when a sequence is generated. Defaults to None.
        """
        step = {"devices":devices,"duration_s":duration_s}
        self.steps.append(step)
    


class Sequence:

    def __init__(self,sequence_subsets:list=None):
        if sequence_subsets == None: 
            self.sequence_subsets = []
        else:
            self.sequence_subsets = sequence_subsets
            
    def add_step(self,devices:list=None,duration:float=None):
        sub_sequence = SequenceSubset()
        sub_sequence.add_step(devices,duration)
        self.sequence_subsets.append(sub_sequence)
    
    def add_sub_sequence(self, sub_sequence:SequenceSubset):
        self.sequence_subsets.append(sub_sequence)

    def __repr__(self):
        response = ""
        for subset in self.sequence_subsets:
            subs = repr(subset)
            response = response + subs
        return response


dev1 = SequenceDevice(0,"device 1")
dev2 = SequenceDevice(1, "device 2")
dev3 = SequenceDevice(2, "device 3")

sub = SequenceSubset()
sub.add_step([dev1,dev2,dev3],10e-9)
sub.add_step([dev2,dev3],20e-9)
sub.add_step([dev1,dev3],30e-9)
print(sub)

seq = Sequence()
seq.add_step([dev1,dev2,dev3],50e-9)
seq.add_sub_sequence(sub)
print(seq)

