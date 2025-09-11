""" 
There was an implementation issue with the sumitomo f70 implementation that will not allow for reconnection 
https://github.com/xkstein/Sumitomo-F70-Python/tree/main
"""

import serial
import sumitomo_f70

class Sumitomof40(sumitomo_f70.SumitomoF70):
    def __init__(self,com_port:int,baudrate:int=9_600, timeout=1,parity=serial.PARITY_NONE, data_bits = 8,stop_bits = 1,flow_control=None,handshaking = None):
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.flow_control = flow_control
        self.handshaking = handshaking

    def __enter__(self,*args,**kwargs):
        
        self.connection = serial.Serial(f"COM{self.com_port}",
                                          baudrate=self.baudrate,
                                          timeout=self.timeout,
                                          parity=self.parity,
                                          stopbits=self.stop_bits,
                                          bytesize=self.data_bits)

    def __exit__(self,*args,**kwargs):
        self.connection.close()