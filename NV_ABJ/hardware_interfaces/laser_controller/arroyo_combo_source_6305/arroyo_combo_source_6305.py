import serial
import time
com_port = "COM8" 
# Setting up and connecting to device
try:
    ser = serial.Serial(port =  com_port,
                                baudrate = 38400,
                                parity =   serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                timeout =  0,
                                write_timeout = 0)
    ser.write(b'*IDN? \r\n')
    time.sleep(0.1)
    # Shows the model of Arroyo Instrument
    print(bytes.decode(ser.read(256)))
except:
    pass
finally:
    ser.close()
