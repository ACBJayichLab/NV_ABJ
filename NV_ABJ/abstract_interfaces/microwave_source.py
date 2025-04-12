__all__ = ["MicrowaveSource","MicrowaveSourceConfiguration"]

from abc import ABCMeta, abstractmethod
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice
import numpy.typing as npt
import numpy as np
from dataclasses import dataclass

@dataclass
class MicrowaveSourceConfiguration:
    frequency_range_hz:tuple[float,float]
    amplitude_range_dbm:tuple[float,float]

class MicrowaveSource(ConnectedDevice,metaclass=ABCMeta):
    """This is a class for a signal generator not limited to but used for control of the RF supplied to the NV and allows for a general 
    implementation for the singal frequency generators 
    """

    @property
    @abstractmethod
    def frequency_range_hz(self)->tuple[float,float]:
        """This is the frequency range that the prime sinusoidal rf is able to generate in 

        Returns:
            tuple[float,float]: (minimum frequency, maximum frequency)
        """

    @property
    @abstractmethod
    def amplitude_range_dbm(self)->tuple[float,float]:
        """This is the amplitude range that the prime sinusoidal rf is able to generate in 

        Returns:
            tuple[float,float]: (minimum amplitude, maximum amplitude)
        """


    @abstractmethod
    def prime_sinusoidal_rf(self,frequency_list_hz:npt.NDArray[np.float64],
                        rf_amplitude_dbm:npt.NDArray[np.float64],
                        *args,**kwargs):
        """This is a generalized function that is meant to allow for an experimental signal generation this 
        is meant to be implemented so the experimental logic for a cwesr, pulsed esr, or tau sweep will work properly.
        Not all actions need to be completed by the device but these are the expected inputs to constrain an arbitrary 
        waveform to the correct sinusoidal signal. This priming is not meant to start the signal but it is meant to queue
        up the frequency list for operation 

        A primed signal means that when a external trigger is applied to the device or device pair it will play the requested frequency 
        - For the SRS SG384 this means the signal is turned on and a microwave switch is expected to be present 
        - For a Keysight AWG the duration is added and we expect the sequence generator to trigger it on for a preset duration 
       
         Args:
            frequency_list_hz (npt.NDArray[np.float64]): A floating point numpy array that consists of the frequency in Hz 
            rf_amplitude_dbm (npt.NDArray[np.float64]): A floating point numpy array of the amplitude of the un-modulated sine wave dBm
        """
        pass

    @abstractmethod
    def turn_on_signal(self):
        """This turns on the signal source as a continuous operation 
        """
        pass 

    @abstractmethod
    def turn_off_signal(self):
        """This turns off the signal source and will not turn off the device 
        """
        pass   
    @abstractmethod
    def iterate_next_waveform(self):
        """This will iterate through the loaded frequency list essentially setting the current frequency to the triggered values
        """
        pass
