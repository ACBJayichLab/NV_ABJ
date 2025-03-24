from abc import ABCMeta, ABC,abstractmethod
from NV_ABJ import ConnectedDevice

class ScannerSingleAxis(ConnectedDevice,metaclass=ABCMeta):
    """A scanner is defined as an item where we both measure the distance and set the distance this may consist of multiple aspects/ devices or simply one device 
    """
    @abstractmethod
    def set_position_m(self,position:float):
        """Sets the goal position in meters 

        Args:
            position (float): Where we ideally will end our position 
        """
        ...
    @abstractmethod
    def get_position_m(self): 
        """ Returns a position in meters for what was measured 
        """
        ...

class XYZScanner(metaclass=ABCMeta):
    ...


