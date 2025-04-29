__all__ = ["MeasurementSequence"]

from abc import ABCMeta, abstractmethod
import numpy.typing as npt
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence

class MeasurementSequence(metaclass=ABCMeta):
    
    @abstractmethod
    def generate_sequence(self,*args,**kwargs)->Sequence:
        """Returns a sequence class that can be imported to a pulse generator and run 
        """
    @abstractmethod
    def counts_to_raw_counts(self, data:npt.NDArray,*args,**kwargs)->tuple[npt.NDArray]:
        """This returns a dict with the numpy arrays separated for what the data represents.
        This is done so a sequence can be more complicated without needing to worry about processing 
        the sequence data. This should return the raw counts for each sequence step **not** kCounts/s

        Returns:
            tuple[NDArray] :The int is the order in the sequence that was called
        """
    
    @abstractmethod
    def counts_to_counts_per_second(self, data:npt.NDArray,*args,**kwargs)->tuple[npt.NDArray]:
        """This returns a dict with the numpy arrays separated for what the data represents.
        This is done so a sequence can be more complicated without needing to worry about processing 
        the sequence data. This should return the raw counts for each sequence step **not** kCounts/s

        Returns:
            tuple[NDArray] :The int is the order in the sequence that was called
        """