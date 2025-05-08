import numpy.typing as npt
import numpy as np

from NV_ABJ.abstract_interfaces.measurement_sequence import MeasurementSequence
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import *
from NV_ABJ.abstract_interfaces.microwave_source import MicrowaveSource

class RabiIq(MeasurementSequence):

    def generate_sequence(self,depopulation_time_s:float,iq_time_s:float,tau_time_s:float,wait_time_s:float,readout_trigger_duration_s:float,readout_time_s:float,green_pulse_duration_s:float,
                          rf_iq_trigger:SequenceDevice,rf_trigger:SequenceDevice,laser_trigger:SequenceDevice,readout_trigger:SequenceDevice) -> Sequence:
        
        """This is a rabi sequence which has a signal followed by a reference"""
        seq = Sequence()

        # signal
        seq.add_step((green_pulse_duration_s)*1e9,                      [laser_trigger])
        seq.add_step((depopulation_time_s-iq_time_s)*1e9,               [])
        seq.add_step((iq_time_s)*1e9,                                   [rf_iq_trigger])
        seq.add_step((tau_time_s)*1e9,                                  [rf_iq_trigger,rf_trigger])
        seq.add_step((iq_time_s)*1e9,                                   [rf_iq_trigger])
        seq.add_step((wait_time_s-iq_time_s)*1e9,                       [])
        seq.add_step((readout_trigger_duration_s)*1e9,                  [laser_trigger,readout_trigger])
        seq.add_step((readout_time_s-readout_trigger_duration_s)*1e9,   [laser_trigger])
        seq.add_step((readout_trigger_duration_s)*1e9,                  [laser_trigger,readout_trigger])


        # reference
        seq.add_step((green_pulse_duration_s)*1e9,                      [laser_trigger])
        seq.add_step((depopulation_time_s)*1e9,                         [])
        seq.add_step((wait_time_s)*1e9,                                 [])
        seq.add_step((readout_trigger_duration_s)*1e9,                  [laser_trigger,readout_trigger])
        seq.add_step((readout_time_s-readout_trigger_duration_s)*1e9,   [laser_trigger])
        seq.add_step((readout_trigger_duration_s)*1e9,                  [laser_trigger,readout_trigger])

        return seq

    def experimental_setup(self, rf_source:MicrowaveSource, frequency_list_hz:npt.NDArray, rf_amplitude_dbm:npt.NDArray, number_of_data_taking_cycles:int)->int:
        """This loads the RF source needed"""
        with rf_source:
            rf_source.prime_sinusoidal_rf(frequency_list_hz=frequency_list_hz, rf_amplitude_dbm=rf_amplitude_dbm)
            rf_source.iterate_next_waveform()
        
        return number_of_data_taking_cycles*2 
    
    def counts_to_raw_counts(self, data:tuple)->tuple[npt.NDArray,npt.NDArray]:
        """Rabi Seq every bin is the same iteration so this is simply where we just get the counts even minus odd indexes. It then separates the dark and signal"""
        signal = np.array(data[::2])
        reference = np.array(data[1::2])

        return signal,reference

    def counts_to_counts_per_second(self, data:tuple, dwell_time_s:float)->npt.NDArray:
        signal, reference = self.counts(data)
        return signal/dwell_time_s, reference/dwell_time_s
