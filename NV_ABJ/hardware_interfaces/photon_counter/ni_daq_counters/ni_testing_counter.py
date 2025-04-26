from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence
from experimental_configuration import apd_trigger_1,pulse_blaster,signal_generator_1,microwave_switch_1
import time
dwell_time_s = 50e-9
trigger_time_ns = 12.5
wait_time_s = 2.5e-6
mw_frequency = 10e6
number_of_counts = 1_000

print(mw_frequency*wait_time_s)

seq = Sequence()
seq.add_step([microwave_switch_1],wait_time_s*1e9)
seq.add_step([apd_trigger_1],trigger_time_ns)
seq.add_step([microwave_switch_1],dwell_time_s*1e9-trigger_time_ns)
seq.add_step([apd_trigger_1],trigger_time_ns)
seq.add_step([microwave_switch_1],wait_time_s*10*1e9)
seq.add_step([apd_trigger_1],trigger_time_ns)
seq.add_step([microwave_switch_1],dwell_time_s*2*1e9-trigger_time_ns)
seq.add_step([apd_trigger_1],trigger_time_ns)


seq_text = pulse_blaster.generate_sequence(seq)
pulse_blaster.stop()
pulse_blaster.load(seq_text)
pulse_blaster.start()

print(seq_text)

signal_generator_1.make_connection()
signal_generator_1.prime_sinusoidal_rf(frequency_list_hz=[mw_frequency],rf_amplitude_dbm=[13.52])
signal_generator_1.iterate_next_waveform()
signal_generator_1.turn_on_signal()


import nidaqmx
from nidaqmx.constants import AcquisitionType, CountDirection, Edge, TaskMode
import numpy as np

print(f"Estimated Time:{number_of_counts*(dwell_time_s+wait_time_s)}")

with nidaqmx.Task() as task:
    channel = task.ci_channels.add_ci_count_edges_chan(
        "PXI1Slot3/ctr0",
        edge=Edge.RISING,
        initial_count=0,
        count_direction=CountDirection.COUNT_UP,
    )
    task.timing.cfg_samp_clk_timing(
        1000, source="/PXI1Slot3/PFI1", sample_mode=AcquisitionType.CONTINUOUS
    )
    channel.ci_count_edges_term = "/PXI1Slot3/PFI0"
    task.control(TaskMode.TASK_COMMIT)

    nums = np.linspace(10,1000,50).astype(int)
    estimated_times = nums*(dwell_time_s+wait_time_s)
    times_taken_2 = np.zeros(len(nums))

    for i,number_of_counts in enumerate(nums):
        # print(estimated_times[i])
        task.start()

        total_read = 0
        start = time.perf_counter()
        edge_counts = task.read(number_of_samples_per_channel=number_of_counts*2,timeout=100)
        final_time = time.perf_counter()-start
        times_taken_2[i] = final_time

        total_read += len(edge_counts)
        task.stop()
        list_counts = np.array(edge_counts[1::2])-np.array(edge_counts[::2])

    print(f"\nAcquired {total_read/2} total samples.")

# for ind,(odd,even) in enumerate(zip(edge_counts[::2],edge_counts[1::2])):
#     list_counts[ind] = even-odd

print(f"Estimated Counts:{mw_frequency*dwell_time_s*1.5}")
print(f"Average Counts:{np.mean(list_counts)}")
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence
from NV_ABJ.hardware_interfaces.photon_counter.ni_daq_counters.ni_photon_counter_daq_controlled import NiPhotonCounterDaqControlled
from experimental_configuration import apd_trigger_1,pulse_blaster,signal_generator_1,microwave_switch_1
import time
dwell_time_s = 400e-9
wait_time_s = 10e-6
mw_frequency = 10e6

photon_counter =  NiPhotonCounterDaqControlled(device_name="PXI1Slot3",counter_pfi="pfi0",trigger_pfi="pfi1")

seq = Sequence()
seq.add_step([microwave_switch_1],wait_time_s*1e9)
seq.add_step([apd_trigger_1],dwell_time_s*1e9)

seq_text = pulse_blaster.generate_sequence(seq)
pulse_blaster.stop()
pulse_blaster.load(seq_text)
pulse_blaster.start()

print(seq_text)

signal_generator_1.make_connection()
signal_generator_1.prime_sinusoidal_rf(frequency_list_hz=[mw_frequency],rf_amplitude_dbm=[13.52])
signal_generator_1.iterate_next_waveform()
signal_generator_1.turn_on_signal()

estimated_times = []
times_taken = []
# print(f"Estimated Time:{number_of_data_taking_cycles*(dwell_time_s+wait_time_s)}")

# number_of_data_taking_cycles = 1_000
# nums = np.linspace(10,100,30)

for number_of_data_taking_cycles in nums:
    with photon_counter as pc:
        start_time = time.perf_counter()
        data = pc.get_counts_raw_when_triggered(dwell_time_s=dwell_time_s,number_of_data_taking_cycles=int(number_of_data_taking_cycles))
        total_time = time.perf_counter()-start_time
        estimated_times.append(number_of_data_taking_cycles*(dwell_time_s+wait_time_s))
        times_taken.append(total_time)
        # print(f"Time Taken:{time.perf_counter()-start_time}")
        # data = pc.get_counts_raw(dwell_time_s=1)
        
signal_generator_1.close_connection()

print(f"expected counts:{dwell_time_s*mw_frequency}")
print(f"Received Counts:{np.mean(data)}")
pulse_blaster.stop()

est = 25_000
print(f"Estimated time for {est} samples is {est*times_taken[-1]/nums[-1]}s")

import matplotlib.pyplot as plt
print(times_taken)
# plt.scatter(nums,times_taken,label="Initial")

plt.scatter(nums,times_taken_2,label="Improved")
plt.scatter(nums,estimated_times,label="Theoretical Minimum")

plt.xlabel("Number of Samples")
plt.ylabel("Total Function Time(s)")
# plt.ylim([0,0.4])
plt.legend()
plt.show()
