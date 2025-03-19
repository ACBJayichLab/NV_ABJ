import math
import nidaqmx.system


import nidaqmx
from nidaqmx.constants import CountDirection, Edge
from nidaqmx.constants import AcquisitionType, TaskMode,TriggerType

import numpy as np
import time

class NiPfi0Counter:

    def __init__(self,slot,ctr = "ctr0",port="port0",pfi="pfi0"):
        self.slot = slot
        self.ctr = ctr
        self.port  = port
        self.pfi = pfi
    
    def get_counts_raw(self,dwell_time):

        # Setting a sample rate based on the dwell time        
        if dwell_time >= pow(10,-1):
            sampling_rate = 10_000
        elif dwell_time < pow(10,-1) and dwell_time >= pow(10,-3):
            sampling_rate = 100_000
        elif dwell_time < pow(10,-3) and dwell_time >= 2*pow(10,-6):
            sampling_rate = 1_000_000

        elif dwell_time < 2*pow(10,-6) and dwell_time >= 2*pow(10,-7):
            sampling_rate = 10_000_000
        else:
            raise Exception("dwell time selected is too small must be greater than 10^-6 seconds")


        number_of_samples = math.ceil(sampling_rate*dwell_time)

        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:
            samp_clk_task.di_channels.add_di_chan(f"{self.slot}/{self.port}")

            samp_clk_task.timing.cfg_samp_clk_timing(sampling_rate,
                                                    sample_mode=AcquisitionType.CONTINUOUS)
            
            samp_clk_task.control(TaskMode.TASK_COMMIT)

            read_task.ci_channels.add_ci_count_edges_chan(f"{self.slot}/{self.ctr}",
                                                        edge=Edge.RISING,
                                                        initial_count=0,
                                                        count_direction=CountDirection.COUNT_UP)
            
            read_task.ci_channels.all.ci_count_edges_term = f"/{self.slot}/{self.pfi}"
            
            read_task.timing.cfg_samp_clk_timing(sampling_rate,
                                                source=f"/{slot}/di/SampleClock",
                                                active_edge=Edge.RISING,
                                                sample_mode=AcquisitionType.FINITE,
                                                samps_per_chan=number_of_samples)
            
            read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            read_task.triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
            read_task.triggers.arm_start_trigger.dig_edge_src = f"/{slot}/di/SampleClock"

            samp_clk_task.start()
            read_task.start()
            edge_counts = 0
            for i in range(number_of_samples):
                edge_counts = read_task.read()

            read_task.stop()
            samp_clk_task.stop()

        return math.floor(edge_counts)
    
    def get_counts_per_second(self,dwell_time):
        edge_counts = self.get_counts_raw(dwell_time)

        return math.floor(edge_counts/dwell_time)



if __name__ == "__main__":

    slot = "PXI1Slot5"
    dwell_time = 2*pow(10,-1)

    counter = NiPfi0Counter(slot)
    print(f"Raw Counts: {counter.get_counts_raw(dwell_time)}")
    print(f"Counts Per Second: {counter.get_counts_per_second(dwell_time)}")

