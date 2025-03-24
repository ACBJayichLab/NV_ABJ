from abc import ABC, abstractmethod
from numpy.typing import NDArray
import numpy as np

class PhotonCounter(ABC):
    """This is a class that all photon counters implemented on the system should follow in order to be utilized 
    """

    @abstractmethod
    def get_counts_raw(dwell_time_ns:int)-> int:
        """This function when implemented should get the raw counts during the dwell time 

        Args:
            dwell_time_ns (int): how long it takes a sample for 

        Returns:
            int: counts during that time 
        """
        ...
    
    @abstractmethod
    def get_counts_per_second(dwell_time_ns:int) ->int:
        """Standard implementation should just call get counts raw and return the divided value by the dwell time 

        Args:
            dwell_time_ns (int): how long it takes a sample for 
        Returns:
            int: counts during that time per second 
            
        """
        ...
    
    @abstractmethod
    def get_counts_raw_when_triggered(dwell_time_ns:int,number_of_data_taking_cycles:int) -> NDArray[np.int64]:
        """ This should wait for a amount of time for a trigger that should be supplied by the sequence generator it then should take data for that amount of time 
        Args:
            dwell_time_ns (int): how long it takes a sample for 
            number_of_data_taking_cycles (int): how many times we let the sequence repeat 

        Returns:
            NDArray[np.int64]: returns a list of the sequences that have been triggered during a dwell time 
        """
    @abstractmethod
    def get_counts_per_second_when_triggered(dwell_time_ns:int,number_of_data_taking_cycles:int) -> NDArray[np.int64]:
        """ Standard implementation should just call get counts raw when triggered and return the divided value by the dwell time 

        Args:
            dwell_time_ns (int): how long it takes a sample for 
            number_of_data_taking_cycles (int): how many times we let the sequence repeat 

        Returns:
            NDArray[np.int64]: returns a list of the sequences that have been triggered during a dwell time 
        """