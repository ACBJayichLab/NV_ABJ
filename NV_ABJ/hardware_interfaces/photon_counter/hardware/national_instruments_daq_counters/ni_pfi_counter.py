import nidaqmx
from nidaqmx.constants import CountDirection, Edge
import time

class NiPfi0Counter:
    pass

slot = "PXI1Slot5"
dwell_time = 1*pow(10,-1)

with nidaqmx.Task() as task:
    channel = task.ci_channels.add_ci_count_edges_chan(
        f"{slot}/ctr0",
        edge=Edge.RISING,
        initial_count=0,
        count_direction=CountDirection.COUNT_UP,
    )
    channel.ci_count_edges_term = f"/{slot}/pfi0"

    task.start()
    time.sleep(dwell_time)#task.wait_until_done(timeout=dwell_time)
    edge_counts = task.read()
    task.stop()
    


print(f"Acquired count: {edge_counts:n}")
print(f"Average {edge_counts/1000/dwell_time} kCounts/S")

