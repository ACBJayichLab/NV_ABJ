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
    print(bytes.decode(ser.read(256)))

    ser.write(b'LASer:LDI? \r\n')
    time.sleep(0.1)
    print(bytes.decode(ser.read(256)))

    ser.write(b'LASer:LDI 500 \r\n')
    time.sleep(0.1)

    ser.write(b'LASer:LDI? \r\n')
    time.sleep(0.1)
    print(bytes.decode(ser.read(256)))
    # Shows the model of Arroyo Instrument
except:
    pass
finally:
    ser.close()
