#
# Copyright (c) 2023 SpinCore Technologies, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *
import math

CLOCK_FREQ = 75.0
MINIMUM_PULSE_LENGTH = 66.6666

# User friendly names for the control bits
TX_ENABLE = 1
TX_DISABLE = 0
PHASE_RESET = 1
NO_PHASE_RESET = 0
DO_TRIGGER = 1
NO_TRIGGER = 0
USE_SHAPE = 1
NO_SHAPE = 0

# Convert a string in the format "time units" to the proper nanosecond count value
def str_to_ns(time, units):
    multiplier = 0
    if units == 'ns': 
        multiplier = 1.0 
 
    elif units == 'us':
        multiplier = 1000.0
    
    elif units == 'ms':
        multiplier = 1000000.0 
    
    elif units == 's':
        multiplier = 1000000000.0
    else:
        print("Invalid pulse length. Please use format: \"time units\", e.g., 10.0 us")
        n = 1
        o = 0
        return o, n
    n = 0
    time = float(time) * multiplier
    return time, n


print("Copyright (c) 2023 SpinCore Technologies, Inc.\n") 
print("This program outputs two square pulses with amplitude, delay between pulses, "
	  "and pulse lengths specified by the user.") 

print("Pulse durations must be specified in the format: \"time units\", e.g., \"10.0 us\"\n") 

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    pause()
    exit(-1)
	 
while True:
    print("") 
    
    #first_pulse_length ***
    n = 0
    while True:
        
        while True:
            try:
                input_s = input("Please enter the first pulse length (minimum 66.6 ns): ")
                parts = input_s.split()
                if len(parts) != 2:
                    raise ValueError("Invalid pulse length. Please use format: \"time units\", e.g., 10.0 us")
                pulse0_length, units = parts
                pulse0_length = float(pulse0_length)
                break
            except ValueError as e:
                print("Invalid input:", e, "")
                
        pulse0_length_print = pulse0_length
        units0 = units
        [pulse0_length, n] = str_to_ns(pulse0_length, units)
        if pulse0_length < MINIMUM_PULSE_LENGTH:
    	    print("Pulse length too short: %f. Minimum pulse length is %f." %(pulse0_length, MINIMUM_PULSE_LENGTH))  
        else:
            if n == 0:
                break
    
    # first_pulse_amplitude
    while True: 
        pulse0_amplitude = float(input("Please enter the first pulse amplitude scale (-1.0 to 1.0): ") )
    	
        if pulse0_amplitude < -1.0 or pulse0_amplitude > 1.0 : 
            print("Pulse amplitude %.2f invalid. Amplitude scale must be between -1.0 and 1.0 inclusive." %pulse0_amplitude) 
        else:
            break
            
    # first_delay_length
    n = 0
    while True:
        
        while True:
            try:
                input_a = input("Please enter the delay between first and second pulses (minimum 66.6 ns): ") 
                parts = input_a.split()
                if len(parts) != 2:
                    raise ValueError("Invalid delay length. Please use format: \"time units\", e.g., 10.0 us")
                delay0, units = parts
                delay0 = float(delay0)
                break
            except ValueError as e:
                print("Invalid input:", e, "")

        delay0_print = delay0
        unitsd0 = units
        [delay0, n] = str_to_ns(delay0, units)
        if delay0 < MINIMUM_PULSE_LENGTH:
    	    print("Delay length too short: %f. Minimum pulse length is %f." %(delay0, MINIMUM_PULSE_LENGTH))  
        else:
            if n == 0:
                break
                
    print("") 
    
    # Second pulse
    # second_pulse_length
    n = 0
    while True:
        
        while True:
            try:
                input_s = input("Please enter the second pulse length (minimum 66.6 ns): ")
                parts = input_s.split()
                if len(parts) != 2:
                    raise ValueError("Invalid pulse length. Please use format: \"time units\", e.g., 10.0 us")
                pulse1_length, units = parts
                pulse1_length = float(pulse1_length)
                break
            except ValueError as e:
                print("Invalid input:", e, "")
        pulse1_length_print = pulse1_length
        units1 = units
        [pulse1_length, n] = str_to_ns(pulse1_length, units)
        if pulse1_length < MINIMUM_PULSE_LENGTH:
    	    print("Pulse length too short: %f. Minimum pulse length is %f." %(pulse1_length, MINIMUM_PULSE_LENGTH))  
        else:
            if n == 0:
                break
    
    # second_pulse_amplitude:
    while True: 
        pulse1_amplitude = float(input("Please enter the second pulse amplitude scale (-1.0 to 1.0): ") )
    	
        if pulse1_amplitude < -1.0 or pulse1_amplitude > 1.0 : 
            print("Pulse amplitude %.2f invalid. Amplitude scale must be between -1.0 and 1.0 inclusive." %pulse1_amplitude) 
        else:
            break
    
    # second_delay_length:
    n = 0
    while True:
        
        while True:
            try:
                input_a = input("Please enter the delay between second and first pulses (minimum 66.6 ns): ") 
                parts = input_a.split()
                if len(parts) != 2:
                    raise ValueError("Invalid delay length. Please use format: \"time units\", e.g., 10.0 us")
                delay1, units = parts
                delay1 = float(delay1)
                break
            except ValueError as e:
                print("Invalid input:", e, "")
        delay1_print = delay1
        unitsd1 = units
        [delay1, n] = str_to_ns(delay1, units)
        if delay1 < MINIMUM_PULSE_LENGTH:
    	    print("Delay length too short: %f. Minimum pulse length is %f." %(delay1, MINIMUM_PULSE_LENGTH))  
        else:
            if n == 0:
                break
    
    print("") 
    	
    print("Pulse 0 - Amplitude: %0.2f, Length: %0.2f %s" % (pulse0_amplitude, pulse0_length_print, units0) )
    print("Delay 0 - Length: %0.2f %s" % (delay0_print, unitsd0))
    print("Pulse 1 - Amplitude: %0.2f, Length: %0.2f %s" % (pulse1_amplitude, pulse1_length_print, units1) )
    print("Delay 1 - Length: %0.2f %s" % ( delay1_print, unitsd1))
    	
    pb_select_board(0)  
    pb_core_clock(CLOCK_FREQ) 
    pb_set_defaults() 
    
    pulse0_phase = 270.0 
    if pulse0_amplitude < 0.0: 
        pulse0_amplitude *= -1.0
        pulse0_phase = 90.0    	 
    
    pulse1_phase = 270.0 
    if pulse1_amplitude < 0.0:  
        pulse1_amplitude *= -1.0 
        pulse1_phase = 90.0 
    	 
    pb_set_amp(pulse0_amplitude, 0) 
    pb_set_amp(pulse1_amplitude, 1) 
    
    # Zero frequency is DC
    pb_start_programming(FREQ_REGS) 
    pb_set_freq(0.0* MHz) 
    pb_stop_programming() 
    
    pb_start_programming(TX_PHASE_REGS) 
    pb_set_phase(pulse0_phase) 
    pb_set_phase(pulse1_phase) 
    pb_stop_programming() 
    
    pb_start_programming(PULSE_PROGRAM) 
    	
    # 90-deg pulse
    start = pb_inst_dds_shape(0, 0, TX_ENABLE, NO_PHASE_RESET, NO_SHAPE, 0, 0x1FF, CONTINUE, 0, pulse0_length) 
    pb_inst_dds_shape(0, 1, TX_DISABLE, PHASE_RESET, NO_SHAPE, 1, 0x00, CONTINUE, 0, delay0) 
    
    # 180-deg pulse
    pb_inst_dds_shape(0, 1, TX_ENABLE, NO_PHASE_RESET, NO_SHAPE, 1, 0x1FF, CONTINUE, 0, pulse1_length) 
    pb_inst_dds_shape(0, 0, TX_DISABLE, PHASE_RESET, NO_SHAPE, 0, 0x0, BRANCH, start, delay1) 
    pb_stop_programming() 
     
    pb_reset() 
    pb_start() 
    
    print("Program has been triggered.") 
    
pb_stop() 

# Release control of the board
pb_close() 
