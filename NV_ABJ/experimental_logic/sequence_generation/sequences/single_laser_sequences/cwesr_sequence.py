import numpy.typing as npt
import numpy as np

from NV_ABJ.abstract_interfaces.measurement_sequence import MeasurementSequence
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import *
from NV_ABJ.abstract_interfaces.microwave_source import MicrowaveSource
from NV_ABJ.abstract_interfaces.pulse_generator import PulseGenerator

class CWESR(MeasurementSequence):

    def generate_sequence(self,readout_time_s:float,readout_trigger_duration_s:float,
                          laser_trigger:SequenceDevice,rf_trigger:SequenceDevice, readout_trigger:SequenceDevice) -> Sequence:
        """This sequrence is simply the runs a trigger with a delay time where the rf is on"""
        seq = Sequence()
        seq.add_step(np.round((readout_time_s-readout_trigger_duration_s)*1e9),  [rf_trigger,laser_trigger])
        seq.add_step(readout_trigger_duration_s*1e9 ,                            [rf_trigger,laser_trigger,readout_trigger])

        return seq


    def experimental_setup(self, rf_source:MicrowaveSource, frequency_list_hz:npt.NDArray, rf_amplitude_dbm:npt.NDArray, *args, **kwargs)->None:
        """This loads the RF source needed"""
        with rf_source:
            rf_source.prime_sinusoidal_rf(frequency_list_hz=frequency_list_hz, rf_amplitude_dbm=rf_amplitude_dbm)
            rf_source.iterate_next_waveform()
    
    def counts_to_raw_counts(self, data:tuple, *args, **kwargs)->npt.NDArray:
        """Cwesr every bin is the same iteration so this is simply where we just get the counts even minus odd indexes"""
        return data

    def counts_to_counts_per_second(self, data:tuple, dwell_time_s:float, *args, **kwargs)->npt.NDArray:
        counts_per_second = data/dwell_time_s
        return counts_per_second
