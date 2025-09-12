from abc import ABCMeta, ABC,abstractmethod
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice


class PhotoDiode(ConnectedDevice,metaclass=ABCMeta):
    @abstractmethod
    def get_laser_power_w(self):
        """Returns the float of the laser power in watts 
        """