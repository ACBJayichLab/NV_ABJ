import zhinst.ziPython as zi
import numpy as np

class ZurichTuningFork:

    def __init__(self,ip_address,name,tf_data_path,device,aux,DAQ=None,port=8004,api_level=6):
        self.ip_address = ip_address
        self.name = name
        self.device = device
        self.port = port
        self.api_level = api_level
        self.tf_data_path = tf_data_path
        self.aux = aux
        if DAQ == None:
            self.DAQ = zi.ziDAQServer(self.ip_address,self.port,self.api_level)
        else:
            self.DAQ = DAQ
    
    def change_frequency(self,frequency):
        self.DAQ.setDouble(f'/dev{self.device}/oscs/0/freq', frequency)
    
    def get_frequency(self):
        return self.DAQ.getDouble(f'/dev{self.device}/oscs/0/freq')

    def sweep(self,low_freq,high_freq,steps,settle_time):
        frequencies = np.linspace(low_freq,high_freq,steps)


    def get_tuning_fork_data(self,poll_length=0.5,poll_timeout = 1):
        self.DAQ.subscribe(self.tf_data_path)
        self.DAQ.sync()
        data = self.DAQ.poll(poll_length,poll_timeout,0,True)
        x_data = data[self.tf_data_path]['timestamp']
        y = data[self.tf_data_path]["y"]
        x = data[self.tf_data_path]["x"]

        y_data = np.sqrt(np.square(y)+np.square(x))
        self.DAQ.unsubscribe("*")

        return x_data,y_data
    
    def change_cutoff_one(self,cutoff):
        self.DAQ.setDouble(f'/dev{self.device}/pids/0/limitlower',cutoff)
    
    def change_cutoff_two(self,cutoff):
        self.DAQ.setDouble(f'/dev{self.device}/pids/0/upperlimit',cutoff)

    def turn_on_pid(self):
        self.DAQ.setInt(f'/dev{self.device}/pids/0/enable',1)

    def turn_off_pid(self):
        self.DAQ.setInt(f'/dev{self.device}/pids/0/enable',0)