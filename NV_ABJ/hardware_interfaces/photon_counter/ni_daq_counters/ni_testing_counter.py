from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence
from experimental_configuration import apd_trigger_1,pulse_blaster,signal_generator_1,microwave_switch_1
import time
dwell_time_s = 200e-9
wait_time_s = 2.5e-6
mw_frequency = 10e6
print(mw_frequency*wait_time_s)

seq = Sequence()
seq.add_step([microwave_switch_1],wait_time_s*1e9)
seq.add_step([apd_trigger_1],50)
seq.add_step([microwave_switch_1],dwell_time_s*1e9-50)
seq.add_step([apd_trigger_1],50)
seq.add_step([microwave_switch_1],wait_time_s*10*1e9)
seq.add_step([apd_trigger_1],50)
seq.add_step([microwave_switch_1],dwell_time_s*2*1e9-50)
seq.add_step([apd_trigger_1],50)


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
from nidaqmx.constants import AcquisitionType, CountDirection, Edge
import numpy as np

number_of_counts = 50_000
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

    task.start()

    total_read = 0
    start = time.perf_counter()
    edge_counts = task.read(number_of_samples_per_channel=number_of_counts*2,timeout=100)
    print(f"Actual Time: {time.perf_counter()-start}")
    total_read += len(edge_counts)
    task.stop()
    list_counts = np.array(edge_counts[1::2])-np.array(edge_counts[::2])
    print(f"\nAcquired {total_read/2} total samples.")

# for ind,(odd,even) in enumerate(zip(edge_counts[::2],edge_counts[1::2])):
#     list_counts[ind] = even-odd

print(f"Estimated Counts:{mw_frequency*dwell_time_s}")
print(f"Average Counts:{np.mean(list_counts)}")