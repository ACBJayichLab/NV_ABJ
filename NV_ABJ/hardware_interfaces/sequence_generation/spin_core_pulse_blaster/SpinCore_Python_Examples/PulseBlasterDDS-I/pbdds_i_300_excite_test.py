# Copyright (c) 2023 SpinCore Technologies, Inc.
#   http://www.spincore.com
#
# This software is provided 'as-is', without any express or implied warranty. 
# In no event will the authors be held liable for any damages arising from the 
# use of this software.
#
# Permission is granted to anyone to use this software for any purpose, 
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented    you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#  
 
##
# pbdds_i_300_excite_test.py
# This program executes an excitation test on the PulseBlasterDDS-I-300. This test will produce a 1 MHz signal on the 
# RF connector for 10 microseconds then turn off for 1 millisecond. It will then repeat this pattern 
# indefinitely.
# pbddsI
#  

CLOCK_FREQ = 75.0

# User friendly names for the control bits
TX_ENABLE = 1
TX_DISABLE = 0
PHASE_RESET = 1
NO_PHASE_RESET = 0

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *
    
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

  
#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Copyright (c) 2023 SpinCore Technologies, Inc.\n")

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
pb_core_clock(CLOCK_FREQ)

print("Clock frequency: %.2lfMHz\n" % CLOCK_FREQ)
print("This example executes an excitation test on the PBDDS-I-300. This test "
            "will produce a 1 MHz signal on for 10 microseconds then turn off for 1 " 
            "millisecond. The program will repeat this pattern indefinitely. The TTL " 
            "outputs are enabled during the pulse and can be used to trigger your " 
            "oscilloscope.\n")

# Program the first 2 frequency registers
pb_start_programming(FREQ_REGS)   
pb_set_freq(1.0 * MHz)   	  # Register 0
pb_set_freq(1.0 * MHz)   	  # Register 1
pb_stop_programming()   

# Program the first 2 phase registers
pb_start_programming(TX_PHASE_REGS)   
pb_set_phase(0.0)   		  # Register 0
pb_set_phase(0.0)   		  # Register 1
pb_stop_programming()   


# Write the pulse program
pb_start_programming(PULSE_PROGRAM)   

#pb_inst_dds(freq, tx_phase, tx_enable, phase_reset, flags, inst, inst_data, length)
start = pb_inst_dds(1, 1, TX_ENABLE, NO_PHASE_RESET, 0x1FF, CONTINUE, 0, 10.0 * us) 
pb_inst_dds(1, 1, TX_DISABLE, PHASE_RESET, 0x000, BRANCH, start, 1.0 * ms)   

pb_stop_programming()   


# Trigger program
pb_reset()   
pb_start()   

# Release control of the board
pb_close()   
pause()   
