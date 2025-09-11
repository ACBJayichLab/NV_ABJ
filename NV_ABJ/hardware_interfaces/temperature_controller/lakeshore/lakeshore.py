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
        return self._ser.readline().decode("ascii").replace("\r\n","")
    
    def get_sensor_name(self,channel):
        self._ser.write((f'INNAME? {channel}\n').encode())
        return self._ser.readline().decode("ascii").replace("\r\n","")
    
    def set_sensor_name(self,channel, name):
        self._ser.write((f'INNAME {channel}, {name}\n').encode())

    def get_temperature_k(self, channel:int):
        self._ser.write((f'KRDG? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def get_sensor_reading(self,channel:int):
        self._ser.write((f'SRDG? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def get_temperature_c(self,channel):
        self._ser.write((f'CRDG? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def set_temperature_k(self,channel:int, temperature:float):
        """ Sets the temperature of the channel
        lakeshore.set_temperature_k(1,300)


        Args:
            channel (int): numbers 1-4 
            temperature (float): floating point for the temperature 
        """
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

    def set_heater_range(self, channel:int, range_value:int):
        """ Sets the heater range 
        lakeshore.set_heater_range(1,1)


        Args:
            channel (int): Channels 1-4 
            range_value (int): 0-3 for channels 1 and 2, 0-1 for channels 3 and 4 
        """
        self._ser.write((f'RANGE {channel},{range_value}\n').encode())

    def get_heater_output_percent(self,channel:int):
        self._ser.write((f'HTR? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii"))
    
    def set_manual_heater(self, channel, percent):
        self._ser.write((f'MOUT {channel},{percent}\n').encode())
    
    def get_manual_heater(self, channel):
        self._ser.write((f'MOUT? {channel}\n').encode())
        return float(self._ser.readline().decode("ascii").replace("\r\n",""))
    
    def get_input_type(self,channel):
        #TODO: This should likely return the enums classes of the different values
        self._ser.write((f'INTYPE? {channel}\n').encode())
        return np.array(self._ser.readline().decode("ascii").replace("\r\n","").split(",")).astype(int)

    def set_input_type(self,channel,sensor_type,auto_range,sensor_range,compensation,units):
        #TODO: These should likely all be enums so that you can only select the valid responses for them 
        self._ser.write((f'INTYPE {channel},{sensor_type},{auto_range},{sensor_range},{compensation},{units}\n').encode())

    def get_curve_number(self,channel):
        self._ser.write((f'INCRV? {channel}\n').encode())
        return self._ser.readline().decode("ascii").replace("\r\n","")

    def set_curve_number(self,channel,curve_number):
        self._ser.write((f'INCRV {channel},{curve_number}\n').encode())

    def get_point_on_curve(self,curve,index):
        self._ser.write((f'CRVPT? {curve},{index}\n').encode())
        return np.array(self._ser.readline().decode("ascii").replace("\r\n","").split(",")).astype(float)
    
    def get_curve_header(self,curve):
        """<name>,<SN>,<format>,<limit value>,<coefficient>
        """
        self._ser.write((f'CRVHDR? {curve}\n').encode())
        # time.sleep(0.1)
        return self._ser.readline().decode("ascii").replace("\r\n","").split(",")
    
    def get_curve_data(self,curve):
        curve_name,serial_number,format,limit_value,coefficient = self.get_curve_header(curve)

        temperature = np.zeros(200)
        sensor_reading = np.zeros(200)

        for i in range(200):
            sense, temp = self.get_point_on_curve(curve,i+1)
            temperature[i]  = temp
            sensor_reading[i] = sense

        return curve_name,serial_number,format,limit_value,coefficient, sensor_reading,temperature


    def check_input_reading(self, channel:int):
        # Bit Bit Weighting Status Indicator
        # 0 1 invalid reading
        # 4 16 temp under range
        # 5 32 temp over range
        # 6 64 sensor units zero
        # 7 128 sensor units over range

        self._ser.write((f'RDGST? {channel}\n').encode())
        return self._ser.readline().decode("ascii")
    
    def get_alarm_status(self, channel):
        self._ser.write((f'ALARMST? {channel}\n').encode())
        return np.array(self._ser.readline().decode("ascii").replace("\r\n","").split(",")).astype(bool)

if __name__ == "__main__":
    import time

    with Lakeshore336(7) as lakeshore:
        # print(lakeshore.get_pid(3))
        # print(lakeshore.get_manual_heater(3))
        # print(lakeshore.get_heater_range(3))
        print(lakeshore.get_set_temperature_k(4))

        # lakeshore.set_temperature_k(1,set_t_a)
        # lakeshore.set_temperature_k(2,set_t_b)
        lakeshore.set_temperature_k(4,200.02333)
        # lakeshore.set_temperature_k(4,set_t_d)
            

        # lakeshore.set_pid(3,125,10,1.1)

        # lakeshore.set_manual_heater(1,12.5)
        # time.sleep(1)
        # print(lakeshore.get_manual_heater(1))

        # print(lakeshore.get_curve_number("a"))
        # print(lakeshore.get_curve_header(22))
        # print(lakeshore.get_alarm_status("a"))
        # print(lakeshore.get_point_on_curve(22,1))
        # start_time = time.perf_counter_ns()
        # for i in range(21,60):
        #     print(lakeshore.get_curve_data(i))
        #     print(i)

    # print(time.perf_counter_ns()-start_time)



