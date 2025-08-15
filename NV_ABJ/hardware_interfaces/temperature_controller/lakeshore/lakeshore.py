
import serial
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice

import numpy as np
class Lakeshore336(ConnectedDevice):
    def __init__(self,com_port:int,baudrate:int=57_600, timeout=1,parity=serial.PARITY_ODD, data_bits = 7,stop_bits = 1,flow_control=None,handshaking = None):
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.flow_control = flow_control
        self.handshaking = handshaking

    def make_connection(self):
        self._ser = serial.Serial(f"COM{self.com_port}",
                                          baudrate=self.baudrate,
                                          timeout=self.timeout,
                                          parity=self.parity,
                                          stopbits=self.stop_bits,
                                          bytesize=self.data_bits)
    
    def close_connection(self):
        self._ser.close()

    def get_id(self):
        self._ser.write((f'*IDN?\n').encode())
        return self._ser.readline().decode("ascii").replace("\n","")
    
    def get_sensor_name(self,channel):
        self._ser.write((f'INNAME? {channel}\n').encode())
        return self._ser.readline().decode("ascii").replace("\n","")
    
    def set_sensor_name(self,channel, name):
        self._ser.write((f'INNAME {channel}, {name}\n').encode())

    def get_temperature_k(self, channel:int):
        self._ser.write((f'KRDG? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def get_sensor_reading(self,channel:int):
        self._ser.write((f'SRDG? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def set_temperature_k(self,channel:int, temperature:float):
        self._ser.write((f'SETP {channel}, {temperature}\n').encode())
    
    def get_set_temperature_k(self,channel:int):
        self._ser.write((f'SETP? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))

    def get_pid(self, channel:int):
        self._ser.write((f'PID? {channel}\n').encode())
        return np.array(self._ser.readline().decode("ascii").replace("+","").split(",")).astype(float)
    
    def set_pid(self,channel:int,p:float,i:float,d:float):
        # PID <output>,<P value>,<I value>,<D value>
        self._ser.write((f'PID {channel},{p},{i},{d}\n').encode())

    def get_heater_range(self, channel:int):
        self._ser.write((f'RANGE? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))

    def set_heater_range(self, channel:int, range:int):
        self._ser.write((f'RANGE {channel},{range}\n').encode())

    def get_heater_output_percent(self,channel:int):
        self._ser.write((f'HTR? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def check_input_reading(self, channel:int):
        # Bit Bit Weighting Status Indicator
        # 0 1 invalid reading
        # 4 16 temp underrange
        # 5 32 temp overrange
        # 6 64 sensor units zero
        # 7 128 sensor units overrange

        self._ser.write((f'RDGST? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    