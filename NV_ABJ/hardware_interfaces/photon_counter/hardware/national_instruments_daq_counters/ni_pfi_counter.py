import math
import nidaqmx.system


import nidaqmx
from nidaqmx.constants import CountDirection, Edge
from nidaqmx.constants import AcquisitionType, TaskMode,TriggerType, READ_ALL_AVAILABLE,LineGrouping

import numpy as np
import time

class NiPfi0Counter:

    def __init__(self,slot,ctr = "ctr0",port="port0",pfi="pfi0",trigger_port=None):
        self.slot = slot
        self.ctr = ctr
        self.port  = port
        self.pfi = pfi
        self.trigger_port = trigger_port
    
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

            edge_counts = 0

            samp_clk_task.start()
            read_task.start()
         
            edge_counts = read_task.read(READ_ALL_AVAILABLE)

            read_task.stop()
            samp_clk_task.stop()

        return math.floor(edge_counts[-1])
    
    def get_counts_per_second(self,dwell_time):
        edge_counts = self.get_counts_raw(dwell_time)

        return math.floor(edge_counts/dwell_time)
    
    def get_raw_counts_when_triggered(self,dwell_time):
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

        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task, nidaqmx.Task() as trigger_task:
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

            trigger_task.di_channels.add_di_chan("Dev1/port0/line0:3", line_grouping=LineGrouping.CHAN_PER_LINE)
            trigger_task.timing.cfg_samp_clk_timing(1_000, sample_mode=AcquisitionType.CONTINUOUS)

            edge_counts = 0
            triggered_events = 0

            trigger_task.start()
            

            while True:

                triggered_events = trigger_task.read(number_of_samples_per_channel=1000)

                if triggered_events > 0:
                    samp_clk_task.start()
                    read_task.start()

                    
                    edge_counts = read_task.read(READ_ALL_AVAILABLE)

                    read_task.stop()
                    samp_clk_task.stop()

                    break

            trigger_task.stop()

        return math.floor(edge_counts)
    

    def get_counts_per_second_when_triggered(self,dwell_time):
        edge_counts = self.get_raw_counts_when_triggered(dwell_time)

        return math.floor(edge_counts/dwell_time)
    
    def testing_digital_wait_count(self):
        with nidaqmx.Task() as task:
            channel = task.ci_channels.add_ci_count_edges_chan(
                f"{slot}/ctr0",
                edge=Edge.RISING,
                initial_count=0,
                count_direction=CountDirection.COUNT_UP,
            )
            channel.ci_count_edges_term = f"/{slot}/pfi14"

            print("Continuously polling. Press Ctrl+C to stop.")
            task.start()

            try:
                edge_counts = 0
                while True:
                    edge_counts = task.read()
                    print(f"Acquired count: {edge_counts:n}", end="\r")
            except KeyboardInterrupt:
                pass
            finally:
                task.stop()
                print(f"\nAcquired {edge_counts:n} total counts.")

if __name__ == "__main__":

    slot = "PXI1Slot4"
    trigger_port = "pfi2"
    pfi = "pfi0"
    ctr = "ctr0"
    port = "port0"
    dwell_time = pow(10,-1)

    # device = nidaqmx.system.device.Device(slot)
    # for tr in device.terminals:
    #     print(tr)

    # counter = NiPfi0Counter(slot,trigger_port=trigger_port)
    # print(f"Raw Counts: {counter.get_counts_raw(dwell_time)}")
    # # print(f"Counts Per Second: {counter.get_counts_per_second(dwell_time)}")
    # # print(f"Counts When Triggered: {counter.get_raw_counts_when_triggered(dwell_time)}")
    # counter.testing_digital_wait_count()

    # Setting a sample rate based on the dwell time        
    # if dwell_time >= pow(10,-1):
    #     sampling_rate = 10_000
    # elif dwell_time < pow(10,-1) and dwell_time >= pow(10,-3):
    #     sampling_rate = 100_000
    # elif dwell_time < pow(10,-3) and dwell_time >= 2*pow(10,-6):
    #     sampling_rate = 1_000_000
    # elif dwell_time < 2*pow(10,-6) and dwell_time >= 2*pow(10,-7):
    #     sampling_rate = 10_000_000
    # else:
    #     raise Exception("dwell time selected is too small must be greater than 10^-6 seconds")


    # number_of_samples = math.ceil(sampling_rate*dwell_time)

    # with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:
    #     samp_clk_task.di_channels.add_di_chan(f"{slot}/{port}")

    #     samp_clk_task.timing.cfg_samp_clk_timing(sampling_rate,
    #                                             sample_mode=AcquisitionType.CONTINUOUS)
        
    #     samp_clk_task.control(TaskMode.TASK_COMMIT)

    #     read_task.ci_channels.add_ci_count_edges_chan(f"{slot}/{ctr}",
    #                                                 edge=Edge.RISING,
    #                                                 initial_count=0,
    #                                                 count_direction=CountDirection.COUNT_UP)
        
    #     read_task.ci_channels.all.ci_count_edges_term = f"/{slot}/{pfi}"
        
    #     read_task.timing.cfg_samp_clk_timing(sampling_rate,
    #                                         source=f"/{slot}/di/SampleClock",
    #                                         active_edge=Edge.RISING,
    #                                         sample_mode=AcquisitionType.FINITE,
    #                                         samps_per_chan=number_of_samples)
        
    #     read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
    #     read_task.triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
    #     read_task.triggers.arm_start_trigger.dig_edge_src = f"/{slot}/di/SampleClock"

    #     edge_counts = 0

    #     samp_clk_task.start()
    #     read_task.start()
        
    #     edge_counts = read_task.read(READ_ALL_AVAILABLE)

    #     read_task.stop()
    #     samp_clk_task.stop()

    # print(math.floor(edge_counts[-1]))

    import nidaqmx
    from nidaqmx.constants import AcquisitionType, CountDirection, Edge

    with nidaqmx.Task() as task:
        channel = task.ci_channels.add_ci_count_edges_chan(
            f"{slot}/ctr0",
            edge=Edge.RISING,
            initial_count=0,
            count_direction=CountDirection.COUNT_UP,
        )
        task.timing.cfg_samp_clk_timing(
            100000, source=f"/{slot}/PFI2", sample_mode=AcquisitionType.CONTINUOUS
        )
        channel.ci_count_edges_term = f"/{slot}/PFI0"

        print("Continuously polling. Press Ctrl+C to stop.")
        task.start()
        previous_count = 0
        total_read = 0

        try:
            
            while True:
                
                edge_counts = task.read()#number_of_samples_per_channel=1)
                #total_read += len(edge_counts)
                
                print(f"Acquired data: {edge_counts-previous_count}", end="\r")
                previous_count = edge_counts
        except KeyboardInterrupt:
            pass
        finally:
            task.stop()
            print(f"\nAcquired {total_read} total samples.")
