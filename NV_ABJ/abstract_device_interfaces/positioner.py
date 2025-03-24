from abc import ABCMeta, abstractmethod
from NV_ABJ import ConnectedDevice

class PositionerSingleAxis(ConnectedDevice,metaclass=ABCMeta):
    """Positioners are different than scanners because of a lack of feedback to the system you move steps which may be consistent 
    but are not necessarily the same distance each step and there is no feedback as to if you did travel the expected motion
    """
    
    @abstractmethod
    def move_positioner(self,direction:bool,steps:float):
        """This moves the positioner by a set number of steps in a direction

        Args:
            direction (bool): If True or 1 is selected than the positioner moves in the the positive direction if the direction is False or 0 it moves in the negative direction
            steps (float): How far the positioner is traveling in its native units 
        """
        ...
    @abstractmethod
    def stop_positioner(self):
        """Stops the motion of the positioner ideally interrupting any commands currently in action 
        """
        ...

class ThreeLongDistancePositioners:
    def __init__(self,positioner1:PositionerSingleAxis,positioner2:PositionerSingleAxis,positioner3:PositionerSingleAxis):
        
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
