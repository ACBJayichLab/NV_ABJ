__all__ = ["PulseGenerator"]

from abc import ABCMeta, abstractmethod
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice

# For asynchronous worker 
import threading 
import time
class PulseGenerator(ConnectedDevice,metaclass=ABCMeta):

    class _StartAsyncWorker(threading.Thread):
        """Class used to by the asynchronous start to thread the function with a delay"""
        def __init__(self,delayed_s:float, start_function:callable, *args, **kwargs):
            super.__init__(*args, **kwargs)
            self.delayed_s = delayed_s
            self.start_function = start_function

        def run(self):
            # Wait for a time
            time.sleep(self.delayed_s)
            # Call start function
            self.start_function()




    def start_asynchronous(self, delayed_s:float)->None:
        """ This function calls the start function after the specified amount of time
        This is used so that the timing of the first pulse can start after the counters are loaded.
        This allows for the timing of the devices to not be inhibited for determining when the first pulse 
        was performed. N

        Needed for non-uniform pulses a.k.a. pulses with multiple different readouts 
        
        Args:
            delayed_s(float): How long the function will wait before starting the pulse blaster
        """
        start_async = PulseGenerator._StartAsyncWorker(delayed_s=delayed_s,start_function=self.start)
        start_async.run()



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