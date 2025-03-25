from dataclasses import dataclass
from enum import IntEnum

class SequenceEdgeTypes(IntEnum):
    SingleRising = 0 # Triggers the device once at the start of duration (Leaves high during duration)
    TwoRising = 1 # Triggers the device at the start and the end of duration (Two pulses )

@dataclass
class SequenceDevice:
    address:str
    device_label:str
    rise_time:float = None
    fall_time:float = None
    edge_type:SequenceEdgeTypes = SequenceEdgeTypes.SingleRising 
    pulse_time_s:float = None # How long the pulse given to the sequence will be if we have a two rising device

    def __str__(self):
        return self.device_label
        

class SequenceSubset:
    
    def __init__(self,steps:list=None,loop_steps=0):
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

            response = response + f"    devices on:{devices}, duration of step: {item["duration"]} s\n"

        return str(response)
    
    def add_step(self,devices:list=None,duration:float=None):
        step = {"devices":devices,"duration":duration}
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
    
    def convert_to_time_state_changes(self):
        time_dict = {}
        time = 0
        print(time)

        for sub_seq in self.sequence_subsets:
            for looped in range(sub_seq.loop_steps+1):
                for step in sub_seq.steps:
                    
                    if step["duration"] != None:
                        time = time + step["duration"]
                        print(time)

                    if step["devices"] != None:
                        current_devices = []
                        for device in step["devices"]:
                            if device.device_label in time_dict:
                                time_dict[device.device_label]["times"].append(time)
                            else:
                                time_dict[device.device_label] = {}
                                time_dict[device.device_label]["times"] = [time]
                                time_dict[device.device_label]["device_class"] = device
                            current_devices.append(device.device_label)
                            
                    else:
                        for device in time_dict:
                            print(device)
                            time_dict[device]["times"].append(time)



        return time_dict

    def __repr__(self):
        response = ""
        for subset in self.sequence_subsets:
            subs = repr(subset)
            response = response + subs
        return response
    

if __name__ == "__main__":

    device_1 = SequenceDevice(address=0,device_label="device1")
    device_2 = SequenceDevice(address=1, device_label= "Device2")

    # sub = SequenceSubset()
    # sub.add_step(devices=[device_1,device_2],duration=11)
    # sub.add_step(devices=[],duration=21)
    # sub.loop_steps = 10
    # print(sub)

    seq = Sequence()
    seq.add_step(devices=[device_1,device_2],duration=10)
    seq.add_step(duration=10)
    seq.add_step(devices=[device_1],duration=3)
    seq.add_step(devices=[device_2],duration=5)


    # seq.add_step(devices=[device_1],duration=20)
    # seq.add_step(devices=[device_2],duration=35)
    # seq.add_sub_sequence(sub)


    # print(seq)
    timing = seq.convert_to_time_state_changes()
    print(timing["device1"]["times"])
    print(timing["Device2"]["times"])

        

