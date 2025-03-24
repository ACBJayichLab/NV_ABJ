import serial

class ArroyoComboSource6305():

    def __init__(self,controller_class):
        self.controller_class = controller_class
        
    @classmethod
    def make_controller(cls,hardware_id):

        # Getting all connected devices
        connected_ports = serial.Serial.tools.list_ports.comports()

        # Finding the com port associated with a hardware id
        for port, desc, hwid in sorted(connected_ports):
            if hardware_id == hwid:
                
                controller_class = serial.Serial(port,
                        baudrate=38400,
                        timeout=2,
                        bytesize=serial.EIGHTBITS,
                        stopbits=serial.STOPBITS_ONE,
                        parity=serial.PARITY_NONE,
                        rtscts=False
                        )
                controller_class.quer
                return cls(controller_class)

    #######################################################################################################################################################
    # Standard Commands 
    #######################################################################################################################################################
    def check_connection(self):
        self.controller_class

if __name__ == "__main__":
    hardware_id = ""

    # Getting all connected devices
    connected_ports = serial.Serial.tools.list_ports.comports()

    # Finding the com port associated with a hardware id
    for port, desc, hwid in sorted(connected_ports):
        if hardware_id == hwid:
                    
            controller_class = serial.Serial(port,
                    baudrate=38400,
                    timeout=2,
                    bytesize=serial.EIGHTBITS,
                    stopbits=serial.STOPBITS_ONE,
                    parity=serial.PARITY_NONE,
                    rtscts=False
                    )
            controller_class.write("*IDN?")
            data = controller_class.read_all()
            print(data)
