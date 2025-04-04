from abc import ABCMeta, ABC,abstractmethod
from numpy.typing import NDArray
import numpy as np

from NV_ABJ import ConnectedDevice


class PhotonCounter(ConnectedDevice,metaclass=ABCMeta):
    """This is a class that all photon counters implemented on the system should follow in order to be utilized 
    """
    def __init__(self):
        ...

    @abstractmethod
    def get_counts_raw(self,dwell_time_s:float)-> int:
        """This function when implemented should get the raw counts during the dwell time 

        Args:
            dwell_time_ns (int): how long it takes a sample for 

        Returns:
            int: counts during that time 
        """
        ...
    
    @abstractmethod
    def get_counts_raw_when_triggered(self,dwell_time_s:float,number_of_data_taking_cycles:int) -> NDArray[np.int64]:
        """ This should wait for a amount of time for a trigger that should be supplied by the sequence generator it then should take data for that amount of time 
        Args:
            dwell_time_ns (int): how long it takes a sample for 
            number_of_data_taking_cycles (int): how many times we let the sequence repeat 

        Returns:
            NDArray[np.int64]: returns a list of the sequences that have been triggered during a dwell time 
        """
    
    def get_counts_per_second_when_triggered(self,dwell_time_s:float,number_of_data_taking_cycles:int) -> NDArray[np.int64]:
        """ Calls get_counts_raw_when_triggered and divides the output by the dwell time  
        Args:
            dwell_time_ns (int): how long it takes a sample for 
            number_of_data_taking_cycles (int): how many times we let the sequence repeat 

        Returns:
            NDArray[np.int64]: returns a list of the sequences that have been triggered during a dwell time 
        """
        return np.round(self.get_counts_raw_when_triggered(dwell_time_s, number_of_data_taking_cycles)/dwell_time_s)
    
    def get_counts_per_second(self,dwell_time_s:float) ->int:
        """Calls get_counts_raw and return the divided value by the dwell time 

        Args:
            dwell_time_ns (int): how long it takes a sample for 
        Returns:
            int: counts during that time per second 
            
        """
        return np.round(self.get_counts_raw(dwell_time_s)/dwell_time_s)