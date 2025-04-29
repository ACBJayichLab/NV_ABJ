__all__ = ["PulseGenerator"]

from abc import ABCMeta, abstractmethod
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice

class PulseGenerator(ConnectedDevice,metaclass=ABCMeta):
    @abstractmethod
    def load(self,sequence)->int:
        """Starts the loaded sequence

        Returns:
            int: 0 if successful 
        """

    @abstractmethod
    def start(self)->int:
        """Starts the loaded sequence

        Returns:
            int: 0 if successful 
        """
    @abstractmethod
    def stop(self)->int:
        """Stops the running sequence

        Returns:
            int: 0 if successful 
        """
    @abstractmethod
    def clear(self)->int:
        """Clears the loaded sequence
        
        Returns:
            int: 0 if successful 
        """

    @abstractmethod
    def generate_sequence(self,sequence_class):
        """Generates a sequence that can be loaded into the loaded sequence 
        """

    @abstractmethod
    def update_devices(self,devices:list)->int:
        """From a list of devices loaded they are then checked for state if the state is True 
        it turns them on if the state is False it turns them off 

        Returns:
            int: 0 if successful 
        """