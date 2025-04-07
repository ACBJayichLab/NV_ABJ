from abc import ABCMeta, abstractmethod

class ConnectedDevice(metaclass=ABCMeta):
    
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
