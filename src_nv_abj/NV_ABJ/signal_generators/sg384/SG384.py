from NV_ABJ.signal_generators import SignalGenerator

import pyvisa
class SG384:
    def __init__(self,gpib_identification,gpib_class):

        self.gpib_identification = gpib_identification
        self.gpib_class = gpib_class

    def modulation_on(self):
        self.gpib_class.write("MODL 1")
    
    def modulation_off(self):
        self.gpib_class.write("MODL 0")
    
    def modulation_state(self):
        return self.gpib_class.query("MODL?")
    
    def modulation_type(self,tpye:int):
        """
        0 = AM
        1 = FM
        2 = PhiM (Phase)
        3 = Sweep
        4 = Pulse
        5 = Blank
        6 = IQ
        """

        self.gpib_class.write(f"TYPE {type}")

    def get_modulation_type(self):
        return self.gpib_class.query("TYPE?")
    
    def iq_modulation_noise(self):
        self.gpib_class.write("QFNC 4")
    
    def iq_modulation_external(self):
        self.gpib_class.write("QFNC 5")

    def get_iq_modulation(self):
        return self.gpib_class.query("QFNC?")
    
    def rf_on(self):
        self.gpib_class.write("ENBR 1")
    
    def rf_off(self):
        self.gpib_class.write("ENBR 0")
    
    def rf_state(self):
        return self.gpib_class.query("ENBR?")
    
    def change_frequency(self,frequency,unit= "MHz"):
        self.gpib_class.write('FREQ '+str(frequency)+' MHz')
    
    def get_frequency(self):
        return self.gpib_class.query("FREQ?")
    
    def change_amplitude_n_type(self,amplitude):
        self.gpib_class.write('AMPR '+str(amplitude))
    
    def get_amplitude(self):
        return self.gpib_class.query("AMPR?")
    
    def change_phase(self,phase):
        self.gpib_class.write('PHAS '+str(phase))
    
    def get_phase(self):
        return self.gpib_class.query("PHAS?")

    def send_frequency_list(self,frequency_list):
        # Sends the list of desired frequencies to the SRS through GPIB
        self.gpib_class.query(f"LSTC? {len(frequency_list)}")
        self.clear_status()

        for ind,f in enumerate(frequency_list):
            command = f"LSTP {ind},{f},N,N,N,N,N,N,N,N,N,N,N,N,N,N"
            self.gpib_class.write(command)
        
        self.gpib_class.write("LSTE 1")
    
    def get_list_point(self,number):
        return self.gpib_class.query(f"LSTP? {number}")

    def get_list_size(self):
        return self.gpib_class.query("LSTS?")
    
    def get_frequency_list(self):
        size_of_list = int(self.get_list_size())
        frequencies = []

        for i in range(size_of_list):
            freq = self.get_list_point(i)
            frequencies.append(float(self.get_list_point(i).replace(",N,N,N,N,N,N,N,N,N,N,N,N,N,N\r\n","")))

        return frequencies

    def trigger_list_item(self):
        # Triggers the next item on the list for the SRS using the DAQ
        self.gpib_class.write("*TRG")
    

    def clear_status(self):
        return self.gpib_class.write("*CLS")
    
    def check_connection(self):
        response =  self.gpib_class.query("*IDN?")
        if "Stanford Research Systems,SG384" in response:
            return response
        else:
            raise Exception("Failed to confirm srs connection id may be incorrect")
    
    
    @classmethod
    def make_gpib_connection(cls,gpib_identification):
        # Takes a daq card id, daq channel, and a gpib id and returns a class to control the srs
        srs = pyvisa.ResourceManager().open_resource(gpib_identification)
        return cls(gpib_identification,srs)


if __name__ == "__main__":

        
    rm = pyvisa.ResourceManager()
    list_data = rm.list_resources()
    print(list_data)

    
    srs_info = "GPIB0::27::INSTR"

    Srs = SG384.make_gpib_connection(srs_info)
    Srs.check_connection()
    Srs.change_frequency(3500)
    print(Srs.get_frequency())
    Srs.change_amplitude_n_type(-100)
    print(Srs.get_amplitude())
    Srs.change_phase(10)
    print(Srs.get_phase())

    Srs.rf_on()
    print(Srs.rf_state())

    Srs.rf_off()
    print(Srs.rf_state())
    
