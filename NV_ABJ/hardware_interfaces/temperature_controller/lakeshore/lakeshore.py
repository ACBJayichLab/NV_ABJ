from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice
import pyvisa
import serial
import numpy as np

class Lakeshore336(ConnectedDevice):
    def __init__(self,gpib_address:str = None, com_port:int = None,baudrate:int=57_600, timeout=1,parity=serial.PARITY_ODD, data_bits = 7,stop_bits = 1,flow_control=None,handshaking = None):
    
    
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.flow_control = flow_control
        self.handshaking = handshaking

        self.gpib_address = gpib_address
        
        # You must either specify a com port or gpib port 
        if gpib_address != None:
            self.gpib_control = True
        elif com_port != None:
            self.gpib_control = False
        else:
            raise ValueError("You must either specify a com port or a gpib port")

    def make_connection(self):
        if self.gpib_control:
            self._rm = pyvisa.ResourceManager()
            self._ser = self._rm.open_resource(self.gpib_address)
        else:
            self._ser = serial.Serial(f"COM{self.com_port}",
                                            baudrate=self.baudrate,
                                            timeout=self.timeout,
                                            parity=self.parity,
                                            stopbits=self.stop_bits,
                                            bytesize=self.data_bits)
    
    def close_connection(self):
        try:
            self._ser.close()
        except:
            pass

        try:
            self._rm.close()
        except:
            pass

    def query_command(self,command:str):
        if self.gpib_control:
            data =  self._ser.query(command)
        else:
            self._ser.write((f"{command}\n").encode())
            data = self._ser.readline().decode("ascii")

        if "," in data:
            return data.replace("\r\n","").replace(" ","").split(",")
        else:
            return data.replace("\r\n","")

    def send_command(self,command:str):
        if self.gpib_control:
            self._ser.write(command)
        else:
            self._ser.write((f"{command}\n").encode())

    def get_id(self):
        return self.query_command('*IDN?')
    
    def get_sensor_name(self,channel):
        return self.query_command((f'INNAME? {channel}'))
    
    def set_sensor_name(self,channel, name):
        self.send_command(f'INNAME {channel}, {name}')

    def get_temperature_k(self, channel:int):
        return float(self.query_command(f'KRDG? {channel}'))
    
    def get_sensor_reading(self,channel:int):
        return float(self.query_command(f'SRDG? {channel}'))
    
    def get_temperature_c(self,channel):
        return float(self.query_command(f'CRDG? {channel}'))
    
    def set_temperature_k(self,channel:int, temperature:float):
        """ Sets the temperature of the channel
        lakeshore.set_temperature_k(1,300)


        Args:
            channel (int): numbers 1-4 
            temperature (float): floating point for the temperature 
        """
        self.send_command(f'SETP {channel}, {temperature}')
    
    def get_set_temperature_k(self,channel:int):
        return float(self.query_command(f'SETP? {channel}'))

    def get_pid(self, channel:int):
        return np.array(self.query_command(f'PID? {channel}')).astype(float)
    
    def set_pid(self,channel:int,p:float,i:float,d:float):
        # PID <output>,<P value>,<I value>,<D value>
        self.send_command(f'PID {channel},{p},{i},{d}\n')

    def get_heater_range(self, channel:int):
        return float(self.query_command(f'RANGE? {channel}'))

    def set_heater_range(self, channel:int, range_value:int):
        """ Sets the heater range 
        lakeshore.set_heater_range(1,1)


        Args:
            channel (int): Channels 1-4 
            range_value (int): 0-3 for channels 1 and 2, 0-1 for channels 3 and 4 
        """
        self.send_command(f'RANGE {channel},{range_value}')

    def get_heater_output_percent(self,channel:int):
        return float(self.query_command(f'HTR? {channel}'))
    
    def set_manual_heater(self, channel, percent):
        self.send_command(f'MOUT {channel},{percent}')
    
    def get_manual_heater(self, channel):
        return float(self.query_command(f'MOUT? {channel}'))
    
    def get_input_type(self,channel):
        #TODO: This should likely return the enums classes of the different values
        return np.array(self.query_command(f'INTYPE? {channel}')).astype(int)

    def set_input_type(self,channel,sensor_type,auto_range,sensor_range,compensation,units):
        #TODO: These should likely all be enums so that you can only select the valid responses for them 
        self.send_command(f'INTYPE {channel},{sensor_type},{auto_range},{sensor_range},{compensation},{units}')

    def get_curve_number(self,channel):
        return self.query_command(f'INCRV? {channel}')

    def set_curve_number(self,channel,curve_number):
        self.send_command(f'INCRV {channel},{curve_number}\n')

    def get_point_on_curve(self,curve,index):
        return np.array(self.query_command(f'CRVPT? {curve},{index}')).astype(float)
    
    def get_curve_header(self,curve):
        """<name>,<SN>,<format>,<limit value>,<coefficient>
        """
        return self.query_command(f'CRVHDR? {curve}')
    
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

        return self.query_command(f'RDGST? {channel}')
    
    def get_alarm_status(self, channel):
        return np.array(self.query_command(f'ALARMST? {channel}')).astype(bool)

 