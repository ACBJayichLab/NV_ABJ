# Numpy is used for array allocation and fast math operations here
import numpy as np
# Used in type hints
from numpy.typing import NDArray

# National instruments daq imports 
import nidaqmx
from nidaqmx.constants import CountDirection, Edge, AcquisitionType, TaskMode,TriggerType, READ_ALL_AVAILABLE



class NationalInstrumentsPhotonCounter:

    def __init__(self,device_name:str,counter_pfi:str,trigger_pfi:str,ctr:str = "ctr0",port:str="port0"):
        """This class is an implementation for a national instruments daq to count the number of photons that we are receiving during an experiment 
        It requires you to define the device name, counter, and the trigger. This works on the premise that the photon counter outputs a digital signal high every time a 
        photon is acquired such that this class can count the digital highs and return them as the photons received 


        photon_counter  =  NationalInstrumentsPhotonCounter(device_name,counter_pfi,trigger_pfi)
        photon_counter  =  NationalInstrumentsPhotonCounter(device_name,counter_pfi,trigger_pfi,ctr,port)

        Args:
            device_name (str): name of the national instruments device for example "PXI1Slot4"
            counter_pfi (str): This is the counter signal that the photon counter is attached to traditionally we attach to "pfi0" on the device_name
            trigger_pfi (str): This is used by the sequence synchronizer so that we can take data for a prescribed time this is usually "pfi#" implemented by using BNC into user# and on the terminal block connecting user# to pfi#
            ctr (str, optional): This is a counter used by the daq. If you have multiple counters running simultaneously on the same device you may need to change this to an available "ctr#". Defaults to "ctr0".
            port (str, optional): This is a digital internal port for counting cycles. If you have multiple counters running simultaneously on the same device you may need to change this to an available "port#". Defaults to "port0".
        """
        self.device_name = device_name
        self.ctr = ctr
        self.port  = port
        self.counter_pfi = counter_pfi
        self.trigger_pfi = trigger_pfi
    
    def get_counts_raw(self,dwell_time_nano_seconds:int,number_of_clock_cycles:int = 2,timeout_waiting_for_data_seconds:float = 60) -> int:
        """get_counts_raw nominally you can call it simply with 
        
            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds)

            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds,number_of_clock_cycles,timeout_waiting_for_data)

        Args:
            dwell_time (int): This is the amount of time in nano seconds that we plan to collect photons 
            number_of_clock_cycles (int, optional): This is the number of clock cycles when sampling data. Defaults to 2.
            timeout_waiting_for_data (float, optional): This is how long the daq will wait for a trigger in this case the trigger is internal and will be activated once loaded. Defaults to 60.

        Raises:
            ValueError: The if the number of clock cycles can not be achieved with the max sampling rate an error is raised 

        Returns:
            int: the raw number of counts that the photon counter has output 
        """


        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:

            # Creating a digital channel that will set the sampling speed for the taken data
            # This is the task that determines how long we sample for so if we have a rate of 100 Hz and take 10 samples
            # The time spent collect photons is 0.1 seconds 
            samp_clk_task.di_channels.add_di_chan(f"{self.device_name}/{self.port}")
            

            # The clock speed does not determine how fast we can count the click it determines how often we check with the daq how many counts have been gotten 
            # Configuring sampling rate and time we need to know our devices max rate to determine if the dwell time is too short 
            max_sampling_rate = samp_clk_task.timing.samp_clk_max_rate

            # finding a clock frequency multiplied the number of cycles to convert to seconds the natural time in the daq
            # The dwell time is modified by adding on cycle of clock time this is to account for a starting count and amounts to the fence post error
            clock_frequency = number_of_clock_cycles*pow(10,9)/(dwell_time_nano_seconds+pow(10,9)/(2*max_sampling_rate)) 
            # Checks if the minimum conditions are reached
            if clock_frequency > max_sampling_rate:
                raise ValueError(f"The selected dwell time does not allow for {number_of_clock_cycles} clock cycles with a max sample rate of {max_sampling_rate}")

            # The sample clock is how we measure time it runs the task for the number of clock cycles desired at the clock frequency to get the measured time 
            samp_clk_task.timing.cfg_samp_clk_timing(clock_frequency,
                                                    sample_mode=AcquisitionType.CONTINUOUS)

            # Saves task to device 
            samp_clk_task.control(TaskMode.TASK_COMMIT)

            # This is connecting a counter to the reading data task 
            read_task.ci_channels.add_ci_count_edges_chan(f"{self.device_name}/{self.ctr}",
                                                        edge=Edge.RISING,
                                                        initial_count=0,
                                                        count_direction=CountDirection.COUNT_UP)
            # We want to count the edges at the pfi provided 
            read_task.ci_channels.all.ci_count_edges_term = f"/{self.device_name}/{self.counter_pfi}"
            # We are taking data for this amount of time based on a digital internal clock set to the clock frequency 
            read_task.timing.cfg_samp_clk_timing(clock_frequency,
                                                source=f"/{self.device_name}/di/SampleClock",
                                                active_edge=Edge.RISING,
                                                sample_mode=AcquisitionType.FINITE,
                                                samps_per_chan=number_of_clock_cycles)
            
            # We want to take the number of counts at the rising edge of the clock 
            read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            read_task.triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
            read_task.triggers.arm_start_trigger.dig_edge_src = f"/{self.device_name}/di/SampleClock"

            # Setting the default amount of counts to 0 
            edge_counts = 0

            # Starting the timing task and the reading tasks
            samp_clk_task.start()
            read_task.start()
        
            # Getting the amount of counts for all cycles 
            edge_counts = read_task.read(READ_ALL_AVAILABLE,timeout=timeout_waiting_for_data_seconds)

            read_task.stop()
            samp_clk_task.stop()

            # Returning the final number of counts 
            return int(edge_counts[-1])
    
    def get_counts_per_second(self,dwell_time_nano_seconds:int,number_of_clock_cycles:int = 2,timeout_waiting_for_data_seconds:float = 60) -> int:
        """get_counts_per_second nominally you can call it simply with 
        
            counts_per_second = photon_counter.get_counts_per_second(dwell_time_nano_seconds)

            counts_per_second = photon_counter.get_counts_per_second(dwell_time_nano_seconds,number_of_clock_cycles,timeout_waiting_for_data)

            internally get_counts_per_second simply calls get_counts_raw and divides by the dwell time

        Args:
            dwell_time (int): This is the amount of time in nano seconds that we plan to collect photons 
            number_of_clock_cycles (int, optional): This is the number of clock cycles when sampling data. Defaults to 10.
            timeout_waiting_for_data (float, optional): This is how long the daq will wait for a trigger in this case the trigger is internal and will be activated once loaded. Defaults to 60.

        Raises:
            ValueError: The if the number of clock cycles can not be achieved with the max sampling rate an error is raised 

        Returns:
            int: the number of counts that the photon counter has output 
        """

        edge_counts = self.get_counts_raw(dwell_time_nano_seconds=dwell_time_nano_seconds,number_of_clock_cycles=number_of_clock_cycles,timeout_waiting_for_data_seconds=timeout_waiting_for_data_seconds)

        return int(edge_counts*pow(10,9)/dwell_time_nano_seconds) # Returns the counts in seconds with the number multiplied to account for nanoseconds 
    
    def get_counts_raw_when_triggered(self,dwell_time_nano_seconds, number_of_data_taking_cycles:int=1, number_of_clock_cycles:int=2, timeout_waiting_for_data_seconds:int=60)-> NDArray[np.int64]:
        """get_counts_raw nominally you can call it simply with 
        
            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds)

            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds,number_of_data_taking_cycles,number_of_clock_cycles,timeout_waiting_for_data)

        Args:
            dwell_time (int): This is the amount of time in nano seconds that we plan to collect photons 
            number_of_clock_cycles (int, optional): This is the number of clock cycles when sampling data. Defaults to 10.
            timeout_waiting_for_data (float, optional): This is how long the daq will wait for a trigger in this case the trigger is internal and will be activated once loaded. Defaults to 60.

        Raises:
            ValueError: The if the number of clock cycles can not be achieved with the max sampling rate an error is raised 

        Returns:
            int: the raw number of counts that the photon counter has output 
        """

        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:

            # Creating a digital channel that will set the sampling speed for the taken data
            # This is the task that determines how long we sample for so if we have a rate of 100 Hz and take 10 samples
            # The time spent collect photons is 0.1 seconds 
            samp_clk_task.di_channels.add_di_chan(f"{self.device_name}/{self.port}")
            

            # The clock speed does not determine how fast we can count the click it determines how often we check with the daq how many counts have been gotten 
            # Configuring sampling rate and time we need to know our devices max rate to determine if the dwell time is too short 
            max_sampling_rate = samp_clk_task.timing.samp_clk_max_rate
            # finding a clock frequency multiplied the number of cycles to convert to seconds the natural time in the daq
            # The dwell time is modified by adding on cycle of clock time this is to account for a starting count and amounts to the fence post error
            clock_frequency = number_of_clock_cycles*pow(10,9)/(dwell_time_nano_seconds+pow(10,9)/(2*max_sampling_rate))             # Checks if the minimum conditions are reached
            if clock_frequency > max_sampling_rate:
                raise ValueError(f"The selected dwell time does not allow for {number_of_clock_cycles} with a max sample rate of {max_sampling_rate}")

            # The sample clock is how we measure time it runs the task for the number of clock cycles desired at the clock frequency to get the measured time 
            samp_clk_task.timing.cfg_samp_clk_timing(clock_frequency,
                                                    sample_mode=AcquisitionType.CONTINUOUS)

            # Saves task to device 
            samp_clk_task.control(TaskMode.TASK_COMMIT)

            # This is connecting a counter to the reading data task 
            read_task.ci_channels.add_ci_count_edges_chan(f"{self.device_name}/{self.ctr}",
                                                        edge=Edge.RISING,
                                                        initial_count=0,
                                                        count_direction=CountDirection.COUNT_UP)
            # We want to count the edges at the pfi provided 
            read_task.ci_channels.all.ci_count_edges_term = f"/{self.device_name}/{self.counter_pfi}"
            # We are taking data for this amount of time based on a digital internal clock set to the clock frequency 
            read_task.timing.cfg_samp_clk_timing(clock_frequency,
                                                source=f"/{self.device_name}/di/SampleClock",
                                                active_edge=Edge.RISING,
                                                sample_mode=AcquisitionType.FINITE,
                                                samps_per_chan=number_of_clock_cycles)
            
            # We want to take the number of counts at the rising edge of the clock 
            read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            read_task.triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
            read_task.triggers.arm_start_trigger.dig_edge_src = f"/{self.device_name}/{self.trigger_pfi}"

            # Setting the default amount of counts to 0 
            edge_counts = 0
            
            # There is one "throw away" cycle due to the fact that we need to initally synchronize the clocks 
            counts_array = np.zeros(number_of_data_taking_cycles+1)

            # Starting the timing task and the reading tasks
            samp_clk_task.start()

            for index,v in enumerate(counts_array):
                read_task.start()
            
                # Getting the amount of counts for all cycles 
                edge_counts = read_task.read(READ_ALL_AVAILABLE,timeout=timeout_waiting_for_data_seconds)
                read_task.stop()
                # Adding the counts to the array
                counts_array[index] = int(edge_counts[-1])

            samp_clk_task.stop()

            # Returning the final number of counts 
            return counts_array[1:]
            

    def get_counts_per_second_when_triggered(self,dwell_time_nano_seconds, number_of_data_taking_cycles:int=1, number_of_clock_cycles:int=2, timeout_waiting_for_data_seconds:int=60)-> NDArray[np.int64]:
        """get_counts_per_second_when_triggered nominally you can call it simply with 
        
            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds)

            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds,number_of_data_taking_cycles,number_of_clock_cycles,timeout_waiting_for_data)

        Args:
            dwell_time (int): This is the amount of time in nano seconds that we plan to collect photons 
            number_of_clock_cycles (int, optional): This is the number of clock cycles when sampling data. Defaults to 10.
            timeout_waiting_for_data (float, optional): This is how long the daq will wait for a trigger in this case the trigger is internal and will be activated once loaded. Defaults to 60.

        Raises:
            ValueError: The if the number of clock cycles can not be achieved with the max sampling rate an error is raised 

        Returns:
            int: the raw number of counts that the photon counter has output 
        """
        edge_counts = self.get_counts_raw_when_triggered(dwell_time_nano_seconds, number_of_data_taking_cycles, number_of_clock_cycles, timeout_waiting_for_data_seconds)

        if number_of_data_taking_cycles == 1:
            return int(edge_counts[0]*pow(10,9)/dwell_time_nano_seconds)
        else:
            return np.floor(edge_counts*pow(10,9)/dwell_time_nano_seconds)
    