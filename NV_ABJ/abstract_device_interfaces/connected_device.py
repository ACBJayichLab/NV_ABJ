from abc import ABCMeta, abstractmethod

class ConnectedDevice(metaclass=ABCMeta):

    @property
    @abstractmethod
    def device_configuration_class(self):
        ...
    
    @abstractmethod
    def make_connection(self):
        ...
    @abstractmethod
    def close_connection(self):
        ...

    ## Enabling the class to be used with "with" 
    def __enter__(self):
        self.make_connection()
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
