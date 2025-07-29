__all__ = ["NiPhotonCounterDaqControlled"]

# Numpy is used for array allocation and fast math operations here
import numpy as np
from numpy.typing import NDArray

# National instruments daq imports 
import nidaqmx
from nidaqmx.constants import CountDirection, Edge, AcquisitionType, TaskMode,TriggerType, READ_ALL_AVAILABLE

# importing abstract class
from NV_ABJ.abstract_interfaces.photon_counter import PhotonCounter
class NiPhotonCounterDaqControlled(PhotonCounter):

    def __init__(self,device_name:str,counter_pfi:str,trigger_pfi:str,ctr:str = "ctr0",port:str  = "port0",number_of_clock_cycles:int = 2,timeout_waiting_for_data_s:int = 60):
        """This class is an implementation for a national instruments daq to count the number of photons that we are receiving during an experiment 
        It requires you to define the device name, counter, and the trigger. This works on the premise that the photon counter outputs a digital signal high every time a 
        photon is acquired such that this class can count the digital highs and return them as the photons received 
        
        Args:
            device_name (str): name of the national instruments device for example "PXI1Slot4"
            counter_pfi (str): This is the counter signal that the photon counter is attached to traditionally we attach to "pfi0" on the device_name
            trigger_pfi (str): This is used by the sequence synchronizer so that we can take data for a prescribed time this is usually "pfi#" implemented by using BNC into user# and on the terminal block connecting user# to pfi#
            ctr (str, optional): This is a counter used by the daq. If you have multiple counters running simultaneously on the same device you may need to change this to an available "ctr#". Defaults to "ctr0".
            port (str, optional): This is a digital internal port for counting cycles. If you have multiple counters running simultaneously on the same device you may need to change this to an available "port#". Defaults to "port0".
            number_of_clock_cycles (int, optional): This is the number of clock cycles when sampling data. We need at least two cycles. Defaults to 2.
            timeout_waiting_for_data (float, optional): This is how long the daq will wait for a trigger in this case the trigger is internal and will be activated once loaded. Defaults to 60.

        """
        self.device_name = device_name
        self.counter_pfi = counter_pfi
        self.trigger_pfi = trigger_pfi

        self.ctr = ctr
        self.port = port
        self.number_of_clock_cycles = number_of_clock_cycles
        self.timeout_waiting_for_data_s = timeout_waiting_for_data_s


    def get_counts_raw(self,dwell_time_s:float) -> int:
        """get_counts_raw nominally you can call it simply with 
        
            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds)

            raw_counts = photon_counter.get_counts_raw(dwell_time_nano_seconds,number_of_clock_cycles,timeout_waiting_for_data)

        Args:
            dwell_time_s (float): This is the amount of time in seconds that we plan to collect photons 
           
        Raises:
            ValueError: The if the number of clock cycles can not be achieved with the max sampling rate an error is raised 

        Returns:
            int: the raw number of counts that the photon counter has output 
        """

        if not self._load_ext_triggered:

            if self.ext_trig_read_task != None:
                self.ext_trig_read_task.close()
                self.ext_trig_read_task = None

            self._load_ext_triggered = True

        # Opens if not preloaded or if the dwell time changes 
        if self._load_self_triggered or self._dwell_time_s != dwell_time_s:

            #If the task is already open we want to close the previous one so we can update it
            if self.samp_clk_task != None:
                try:
                    self.samp_clk_task.close()
                except:
                    pass
                self.samp_clk_task = None

            if self.read_task != None:
                try:
                    self.read_task.close()
                except:
                    pass
                self.read_task = None

            # Creating tasks to run
            self.read_task = nidaqmx.Task() 
            self.samp_clk_task =  nidaqmx.Task()

            # Creating a digital channel that will set the sampling speed for the taken data
            # This is the task that determines how long we sample for so if we have a rate of 100 Hz and take 10 samples
            # The time spent collect photons is 0.1 seconds 
            self.samp_clk_task.di_channels.add_di_chan(f"{self.device_name}/{self.port}")

            # Determining the maximum sample rate linked to the clock frequency
            self.max_sampling_rate = self.samp_clk_task.timing.samp_clk_max_rate
        
            # Default triggering steps
            self.samp_clk_task.triggers.start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            self.samp_clk_task.triggers.start_trigger.dig_edge_edge = Edge.RISING
            


            # This is connecting a counter to the reading data task 
            self.read_task.ci_channels.add_ci_count_edges_chan(f"{self.device_name}/{self.ctr}",
                                                        edge=Edge.RISING,
                                                        initial_count=0,
                                                        count_direction=CountDirection.COUNT_UP)
            
            # We want to count the edges at the pfi provided 
            self.read_task.ci_channels.all.ci_count_edges_term = f"/{self.device_name}/{self.counter_pfi}"
            
            # We want to take the number of counts at the rising edge of the clock 
            self.read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            self.read_task.triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
            self.read_task.triggers.arm_start_trigger.dig_edge_src = f"/{self.device_name}/di/SampleClock"

            # finding a clock frequency multiplied the number of cycles to convert to seconds the natural time in the daq
            # The dwell time is modified by adding on cycle of clock time this is to account for a starting count and amounts to the fence post error
            clock_frequency = self.number_of_clock_cycles/(dwell_time_s+1/(2*self.max_clock)) 
            # Checks if the minimum conditions are reached
            if clock_frequency > self.max_sampling_rate:
                raise ValueError(f"The selected dwell time does not allow for {self.number_of_clock_cycles} clock cycles with a max sample rate of {self.max_sampling_rate}")

            # The sample clock is how we measure time it runs the task for the number of clock cycles desired at the clock frequency to get the measured time 
            self.samp_clk_task.timing.cfg_samp_clk_timing(clock_frequency,
                                                    sample_mode=AcquisitionType.CONTINUOUS)

            self.samp_clk_task.triggers.start_trigger.dig_edge_src = f"/{self.device_name}/{self.timebase}"

            



            # We are taking data for this amount of time based on a digital internal clock set to the clock frequency 
            self.read_task.timing.cfg_samp_clk_timing(rate = clock_frequency,
                                                source=f"/{self.device_name}/di/SampleClock",
                                                active_edge=Edge.RISING,
                                                sample_mode=AcquisitionType.FINITE,
                                                samps_per_chan=self.number_of_clock_cycles)
            
            # Saves task to device 
            self.samp_clk_task.control(TaskMode.TASK_COMMIT)
            self.read_task.control(TaskMode.TASK_COMMIT)

            self._load_self_triggered = False
            self._dwell_time_s = dwell_time_s
 



        # Setting the default amount of counts to 0 
        edge_counts = 0

        # Starting the timing task and the reading tasks
        self.samp_clk_task.start()
        self.read_task.start()
    
        # Getting the amount of counts for all cycles 
        edge_counts = self.read_task.read(READ_ALL_AVAILABLE,timeout=self.timeout_waiting_for_data_s)[-1]
        self.read_task.wait_until_done()

        self.read_task.stop()
        self.samp_clk_task.stop()

        # Returning the final number of counts 
        return edge_counts       
    
    def get_counts_raw_when_triggered(self, number_of_data_taking_cycles:int, continuous_line:bool = False, double_samples = True)-> NDArray[np.int64]:
        """get_counts_raw nominally you can call it simply with 
        
            raw_counts = photon_counter.get_counts_raw(number_of_data_taking_cycles)

        Args:
            number_of_data_taking_cycles (int): This is the number of cycles when where samples will be taken and is how long the list will be 
            continuous_line(bool, optional): Defaults to False. This is false if you want the counts between two points and true if you want the counts at every trigger

        Raises:
            ValueError: The if the number of clock cycles can not be achieved with the max sampling rate an error is raised 

        Returns:
            int: the raw number of counts that the photon counter has output 
        """
        if not self._load_self_triggered:

            if self.read_task != None:
                self.read_task.close()
                self.read_task = None
                self._dwell_time_s = None
            
            if self.samp_clk_task != None:
                self.samp_clk_task.close()
                self.samp_clk_task = None

            self._load_self_triggered = True

        if self._load_ext_triggered:
            self.ext_trig_read_task = nidaqmx.Task()
            channel = self.ext_trig_read_task.ci_channels.add_ci_count_edges_chan(
                f"{self.device_name}/{self.ctr}",
                edge=Edge.RISING,
                initial_count=0,
                count_direction=CountDirection.COUNT_UP,
            )

            # This is a buffered task so it doesn't require a fast clock 
            self.ext_trig_read_task.timing.cfg_samp_clk_timing(self.max_clock,
                                                      source=f"/{self.device_name}/{self.trigger_pfi}",
                                                        sample_mode=AcquisitionType.CONTINUOUS)
            
            channel.ci_count_edges_term = f"/{self.device_name}/{self.counter_pfi}"
            self.ext_trig_read_task.control(TaskMode.TASK_COMMIT)
            self._load_ext_triggered = False
        
        if double_samples:
            number_of_data_taking_cycles = number_of_data_taking_cycles*2
            
        self.ext_trig_read_task.start()
        edge_counts = self.ext_trig_read_task.read(number_of_samples_per_channel=number_of_data_taking_cycles,timeout=self.timeout_waiting_for_data_s)
        self.ext_trig_read_task.stop()

        if not continuous_line:
            list_counts = np.array(edge_counts[1::2])-np.array(edge_counts[::2])
        else:
            list_counts = edge_counts

        return list_counts

    
    def make_connection(self):
        """ Makes a connection to the task. This would normally be handled by the daq but it's been unwrapped here for time on repeated operations
        """
        self._load_self_triggered = True
        self._load_ext_triggered = True


        # The clock speed does not determine how fast we can count the click it determines how often we check with the daq how many counts have been gotten 
        # Configuring sampling rate and time we need to know our devices max rate to determine if the dwell time is too short 
        self.max_clock = nidaqmx.system.device.Device(self.device_name).ci_max_timebase

        # Determining the timebase 
        if self.max_clock >= 1e9:
            self.timebase = f"{int(self.max_clock*(1e-9))}GHzTimebase"
        elif self.max_clock < 1e9 and self.max_clock >= 1e6:
            self.timebase = f"{int(self.max_clock*(1e-6))}MHzTimebase"
        elif self.max_clock < 1e6 and self.max_clock >= 1e3:
            self.timebase = f"{int(self.max_clock*(1e-3))}kHzTimebase"
        else:
            raise ValueError("Unknown time base for sample clock")
        
        self.samp_clk_task = None
        self.read_task = None
        self.ext_trig_read_task = None
        self._dwell_time_s = None


    def close_connection(self):
        """Closes the tasks that have been opened 
        """
        self._load_self_triggered = True
        self._load_ext_triggered = True

        if self.read_task != None:
            self.read_task.close()
            self.read_task = None
        
        if self.samp_clk_task != None:
            self.samp_clk_task.close()
            self.samp_clk_task = None
        
        if self.ext_trig_read_task != None:
            self.ext_trig_read_task.close()
            self.ext_trig_read_task = None


    @property
    def __repr__(self):
        response = f"""Device Name: {self.device_name},
                       Counter PFI: {self.counter_pfi}, 
                       Trigger PFI: {self.trigger_pfi},
                       Counter: {self.ctr},
                       Port: {self.port},
                       Timeout Time (s):{self.timeout_waiting_for_data_s}"""
        return response
    

if __name__ == "__main__":
    photon_counter_1 = NiPhotonCounterDaqControlled(device_name="PXI1Slot2",
                                                        counter_pfi="pfi0",
                                                        trigger_pfi="pfi13")
    
    with photon_counter_1 as pc:
        for i in range(20,100):
            print(pc.get_counts_per_second(i*1e-3))