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
    times_taken = np.zeros(len(nums))

    for i,number_of_counts in enumerate(nums):
        # print(estimated_times[i])
        task.start()

        total_read = 0
        start = time.perf_counter()
        edge_counts = task.read(number_of_samples_per_channel=number_of_counts*2,timeout=100)
        final_time = time.perf_counter()-start
        times_taken[i] = final_time

        total_read += len(edge_counts)
        task.stop()
        list_counts = np.array(edge_counts[1::2])-np.array(edge_counts[::2])

    print(f"\nAcquired {total_read/2} total samples.")

# for ind,(odd,even) in enumerate(zip(edge_counts[::2],edge_counts[1::2])):
#     list_counts[ind] = even-odd

print(f"Estimated Counts:{mw_frequency*dwell_time_s*1.5}")
print(f"Average Counts:{np.mean(list_counts)}")

import matplotlib.pyplot as plt

plt.scatter(nums,times_taken,label="Actual")
plt.scatter(nums,estimated_times,label="Est")
plt.xlabel("Number of Samples")
plt.ylabel("Time(s)")
plt.ylim([0,0.4])
plt.legend()
plt.show()