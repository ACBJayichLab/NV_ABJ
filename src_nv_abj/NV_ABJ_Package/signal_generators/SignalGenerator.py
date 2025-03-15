from abc import abstractmethod
#from qudi.core import Base

class SignalGenerator:#(Base):

    @abstractmethod
    def set_frequency(self,val):
        pass

    def tester():
        print("Yes it worked")