from abc import ABCMeta, abstractmethod
from NV_ABJ import ConnectedDevice

class LongDistancePositionerSingleAxis(ConnectedDevice,metaclass=ABCMeta):
    
    @abstractmethod
    def move_positioner(self,direction,steps):
        ...
    @abstractmethod
    def stop_positioner(self):
        ...

class ThreeLongDistancePositioners:
    def __init__(self,positioner1:LongDistancePositionerSingleAxis,positioner2:LongDistancePositionerSingleAxis,positioner3:LongDistancePositionerSingleAxis):
        
        self.positioner1 = positioner1
        self.positioner2 = positioner2
        self.positioner3 = positioner3

    def move_positioner1(self, direction, steps):
        self.positioner1.move_positioner(direction,steps)
    
    def move_positioner2(self, direction, steps):
        self.positioner2.move_positioner(direction,steps)
    
    def move_positioner3(self, direction, steps):
        self.positioner3.move_positioner(direction,steps)

    def stop(self):
        """Calls stop positioner for all connected positioners 
        """
        for positioner in self.positioners:
            positioner.stop_positioner()
