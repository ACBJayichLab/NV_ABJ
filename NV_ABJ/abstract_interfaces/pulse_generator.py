__all__ = ["PulseGenerator"]

from abc import ABCMeta, abstractmethod
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice

# For asynchronous worker 
import threading 
import time
import multiprocessing

class PulseGenerator(ConnectedDevice,metaclass=ABCMeta):

    def _start_asynchronous_worker(self,delayed_s:float):
            # Wait for a time
            print("Waiting Time")
            time.sleep(self.delayed_s)

            # Call start function
            self.start()
            print("Starting Function")



    def start_asynchronous(self, delayed_s:float)->None:
        """ This function calls the start function after the specified amount of time
        This is used so that the timing of the first pulse can start after the counters are loaded.
        This allows for the timing of the devices to not be inhibited for determining when the first pulse 
        was performed. N

        Needed for non-uniform pulses a.k.a. pulses with multiple different readouts 
        
        Args:
            delayed_s(float): How long the function will wait before starting the pulse blaster
        """
        start_async = multiprocessing.Process(target=self._start_asynchronous_worker, args=(delayed_s,))
        start_async.start()



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