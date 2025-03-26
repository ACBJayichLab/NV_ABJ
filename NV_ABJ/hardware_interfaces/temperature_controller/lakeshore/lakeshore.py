import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())

lakeshore_address = 'GPIB0::12::INSTR'
lakeshore = rm.open_resource(lakeshore_address)
print(lakeshore.query("*IDN?")) # Gets id 
channel = "d" # a,b,c,d
print(lakeshore.query(f"INNAME? {channel}")) # Gets channel name 
print(lakeshore.query(f"KRDG? {channel}")) # Gets the current reading in kelvin
print(lakeshore.query(f"ALARM? {channel}")) # Gets the channel alarm 
lakeshore.close()

