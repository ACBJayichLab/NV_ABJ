# Copyright (c) 2023 SpinCore Technologies, Inc.
# http:    www.spincore.com
#
# This software is provided 'as-is', without any express or implied warranty. 
# In no event will the authors be held liable for any damages arising from the 
# use of this software.
#
# Permission is granted to anyone to use this software for any purpose, 
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#  
 
##
# \file DirectCapture.py
# 
# \brief This program demonstrates how to use the Direct Ram Capture feature of the 
# RadioProcessor.
# NOTE: This feature is only enabled in the PCI RadioProcessor with Firmware Revisions
# 10-14 and up and USB RadioProcessors with Firmware Revisions 12-5 and up.
# \ingroup RP
#  

# Defines for easy reading.
RAM_SIZE = (16*1024)
BOARD_STATUS_IDLE = 0x3
DO_TRIGGER = 1
NO_TRIGGER = 0
ADC_FREQUENCY= 75.0

# The number of points your board will acquire.
# For PCI boards, the full ram size is 16384 points.  For USB boards it is 4*16384 points.
NUMBER_POINTS = int(4*16384)

# The number of scans to perform (with signal averaging enabled.)
# If you use signal averaging, please make sure that there is phase coherence between scans.
NUMBER_SCANS = 1

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *
import ctypes

def pause():
    input("Press enter to continue...")
    
def detect_boards():
    global numBoards
    
    numBoards = pb_count_boards()
    
    if numBoards <= 0:
        print("No Boards were detected in your system. Verify that the board "
       "is firmly secured in the PCI slot.\n")
        pause()
        exit(-1)
        
def select_boards():
    while True:
        try:
            choice = int(input(f"Found {numBoards} boards in your system. Which board should be used? (0-{numBoards-1}): "))
            if choice < 0 or choice >= numBoards:
                print("Invalid Board Number (%d)." % choice)
            else:
                pb_select_board(choice)
                print("Board %d selected." % choice)
                break;
        except ValueError:
            print("Incorrect input. Please enter a valid board number.")


# These variables are used for the Title Block in Felix  
program_type = "DirectCapture"
data = (ctypes.c_short*NUMBER_POINTS)()
data_imag =(ctypes.c_short*NUMBER_POINTS)()
idata = [0]*NUMBER_POINTS
idata_imag = [0]*NUMBER_POINTS

#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Using SpinAPI Library version %s" % pb_get_version())

# If there is more than one board in the system, have the user specify. 
detect_boards()

if numBoards > 1:
    select_boards()

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    pause()
    exit(-1)

pb_set_defaults()
pb_core_clock(ADC_FREQUENCY) # Set the PulseBlaster Core Operating frequency.
pb_overflow(1,0) # Reset the overflow counters.
pb_scan_count(1) # Reset scan counter.

pb_set_radio_control(RAM_DIRECT) # Enable direct ram capture.

pb_set_num_points(NUMBER_POINTS) # This is the number of points that we are going to be capturing.

wait_time = 1000.0 * (NUMBER_POINTS) / (ADC_FREQUENCY * 1e6) # Time in ms

pb_start_programming(PULSE_PROGRAM)
start = pb_inst_radio_shape(0, 0, 0, 0, 0, 0, NO_TRIGGER, 0, 0, 0x02, LOOP, NUMBER_SCANS, 1.0 * us)
pb_inst_radio_shape(0, 0, 0, 0, 0, 0, DO_TRIGGER, 0, 0, 0x01, END_LOOP, start, wait_time * ms)
pb_inst_radio_shape(0, 0, 0, 0, 0, 0, NO_TRIGGER, 0, 0, 0x02, STOP, 0, 1.0 * us)
pb_stop_programming()

print("Performing direct ram capture...");

pb_reset()
pb_start()

print("Waiting for the data acquisition to complete.")

while pb_read_status() != BOARD_STATUS_IDLE: # Wait for the board to complete execution.
    pb_sleep_ms(100)
      
pb_get_data_direct(NUMBER_POINTS,data)
pb_unset_radio_control(RAM_DIRECT)	# Disable direct ram capture.

pb_close()

#pb_write_ascii ("direct_data.txt", NUMBER_POINTS, 1.0, idata, idata_imag);
	
fp_ascii = open("direct_data.txt","w")

for i in range(NUMBER_POINTS):
    fp_ascii.write(str(data[i]) + "\n")

fp_ascii.close()

# The spectrometer frequency does not matter in a direct ram capture. Using 1.0 MHz for
# proper file format.
  
# Create Title Block String
title_string = "Program = " + program_type

for i in range(NUMBER_POINTS):
    idata[i] = data[i]
    idata_imag[i] = data_imag[i]  
      
pb_write_felix("direct_data.fid", title_string, NUMBER_POINTS, ADC_FREQUENCY * 1e6, 1.0, idata, idata_imag)

pause()
