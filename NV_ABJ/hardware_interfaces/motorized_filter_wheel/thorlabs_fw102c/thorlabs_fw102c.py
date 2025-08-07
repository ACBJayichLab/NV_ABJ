import serial
from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice

class FW102C(ConnectedDevice):
    def __init__(self,com_port:int,wheel_type:int,baudrate:int=115200, timeout=1):
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.wheel_type = wheel_type
    
    def make_connection(self):
        self._ser = serial.serial_for_url(f"COM{self.com_port}",baudrate=self.baudrate,timeout=self.timeout)
    
    def close_connection(self):
        self._ser.close()
    
    def get_id(self):
        self._ser.write((f'*idn?\r').encode())
        return self._ser.readline().decode("ascii")
    
    def get_speed(self):
        self._ser.write((f'speed?\r').encode())
        count = self._ser.readline().replace(b"\r",b"\n").decode('utf-8').split("\n")
        try:
            n_count = int(count[1])
            return n_count
        except Exception as e:
            raise Exception(f"Failed to get valid response:{count},Error:{e}")


    def high_speed(self):
        self._ser.write((f'speed=1\r').encode())

    def low_speed(self):
        self._ser.write((f'speed=0\r').encode())

    def get_sensor(self):
        self._ser.write((f'sensors?\r').encode())
        count = self._ser.readline().replace(b"\r",b"\n").decode('utf-8').split("\n")
        try:
            n_count = int(count[1])
            return n_count
        except Exception as e:
            raise Exception(f"Failed to get valid response:{count},Error:{e}")


    def sensor_off_when_idle(self):
        self._ser.write((f'sensors=0\r').encode())

    def sensor_always_on(self):
        self._ser.write((f'sensors=1\r').encode())

    def get_baud(self):
        self._ser.write((f'baud?\r').encode())
        baud = self._ser.readline().replace(b"\r",b"\n").decode('utf-8').split("\n")
        try:
            n_baud = int(baud[1])
            if n_baud == 0:
                return 9600
            elif n_baud == 1:
                return 115200
            else:
                raise ValueError(f"Response failed:{baud}")
        except Exception as e:
            raise Exception(f"Failed to get valid response:{baud},Error:{e}")

    
    def set_baud_9600(self):
        self._ser.write((f'baud=0\r').encode())

    def set_baud_115200(self):
        self._ser.write((f'baud=1\r').encode())

    def get_trigger(self):
        self._ser.write((f'trig?\r').encode())
        count = self._ser.readline().replace(b"\r",b"\n").decode('utf-8').split("\n")
        try:
            n_count = int(count[1])
            return n_count
        except Exception as e:
            raise Exception(f"Failed to get valid response:{count},Error:{e}")

    def set_external_trigger_to_input(self):
        self._ser.write((f'trig=0\r').encode())

    def set_external_trigger_to_output(self):
        self._ser.write((f'trig=1\r').encode())

    def get_wheel_type(self):
        self._ser.write((f'pcount?\r').encode())
        count = self._ser.readline().replace(b"\r",b"\n").decode('utf-8').split("\n")
        try:
            n_count = int(count[1])
            return n_count
        except Exception as e:
            raise Exception(f"Failed to get valid response:{count},Error:{e}")
    
    def set_wheel_type_6(self):
        self._ser.write((f'pcount=6\r').encode())

    def set_wheel_type_12(self):
        self._ser.write((f'pcount=12\r').encode())
    
    def get_position(self):
        self._ser.write((f'pos?\r').encode())
        count = self._ser.readline().replace(b"\r",b"\n").decode('utf-8').split("\n")
        try:
            n_count = int(count[1])
            return n_count
        except Exception as e:
            raise Exception(f"Failed to get valid response:{count},Error:{e}")

    def set_position(self,n:int):
        if n >= 1 and n <= self.wheel_type:
            self._ser.write((f'pos={n}\r').encode())
        else:
            raise ValueError("You can not enter a number less than 1 or greater than the wheel type")

    def save_settings(self):
       self._ser.write((f'save\r').encode()) 
