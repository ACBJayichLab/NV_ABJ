import serial
import numpy as np

from NV_ABJ.abstract_interfaces.connected_device import ConnectedDevice

class EdwardsTIC(ConnectedDevice):
    def __init__(self,com_port:int, baudrate:int = 9600):
        self.com_port = com_port
        self.baudrate = baudrate
    
    def make_connection(self):
        self._ser = serial.serial_for_url(f"COM{self.com_port}",
                                          baudrate=self.baudrate)
    
    def close_connection(self):
        self._ser.close()

    def query_command(self,command):
        self._ser.write(str("?"+command+"\r").encode("ascii"))
        response = self._ser.read_until(b"\r").decode("ascii")
        values = np.array(response.replace(f"={command } ","").replace("\r","").split(";")).astype(str)
        return values
    
    def send_command(self,command,value):
        self._ser.write(str(f"!{command} {value}\r").encode("ascii"))
    
    def get_pressure_gauge_1(self):
        pressure_reading, pressure_units, pressure_voltage, pressure_alert, pressure_priority = self.query_command("V913") # Gauge reading, units, state, alert id
        return pressure_reading, pressure_units, pressure_voltage, pressure_alert, pressure_priority
    
    def get_pressure_gauge_2(self):
        pressure_reading, pressure_units, pressure_voltage, pressure_alert, pressure_priority = self.query_command("V914") # Gauge reading, units, state, alert id
        return pressure_reading, pressure_units, pressure_voltage, pressure_alert, pressure_priority
    
    def get_pressure_gauge_3(self):
        pressure_reading, pressure_units, pressure_voltage, pressure_alert, pressure_priority = self.query_command("V915") # Gauge reading, units, state, alert id
        return pressure_reading, pressure_units, pressure_voltage, pressure_alert, pressure_priority
    
    def get_turbo_status(self):
        turbo_status, turbo_status_alert, turbo_status_priority = self.query_command("V904") # Turbo status, alert id, priority 
        return turbo_status, turbo_status_alert, turbo_status_priority

    def get_turbo_speed(self):
        turbo_speed, turbo_speed_alert, turbo_speed_priority = self.query_command("V905") # Turbo Speed Value, alert id, priority 
        return turbo_speed, turbo_speed_alert, turbo_speed_priority 

    def get_turbo_power(self):
        turbo_power, turbo_power_alert, turbo_power_priority = self.query_command("V906") # Turbo Power, alert id, priority
        return turbo_power, turbo_power_alert, turbo_power_priority
    
    def get_turbo_time(self):
        turbo_on_time, turbo_state, turbo_on_time_alert, turbo_on_time_priority = self.query_command("V909") # Turbo time on, alert id, priority 
        return turbo_on_time, turbo_state, turbo_on_time_alert, turbo_on_time_priority
    
    def get_backing_power(self):
        backing_power, backing_power_alert, backing_power_priority = self.query_command("V912") # Backing Power, alert id, priority 
        return backing_power, backing_power_alert, backing_power_priority
    
    def get_backing_status(self):
        backing_status, backing_status_alert, backing_status_priority = self.query_command("V910") # Backing pump Status, alert, priority 
        return backing_status, backing_status_alert, backing_status_priority

    def get_backing_speed(self):
        backing_speed, backing_speed_alert, backing_speed_priority = self.query_command("V911") # Backing speed, alert, id, priority 
        return backing_speed, backing_speed_alert, backing_speed_priority 
    
    def turn_turbo_on(self):
        self.send_command("C904",1)

    def turn_turbo_off(self):
        self.send_command("C904",0)

    def turn_backing_on(self):
        self.send_command("C910",1)

    def turn_backing_off(self):
        self.send_command("C910",0)

if __name__ == "__main__":
    with EdwardsTIC(5) as ed:
        print(ed.query_command("S924"))