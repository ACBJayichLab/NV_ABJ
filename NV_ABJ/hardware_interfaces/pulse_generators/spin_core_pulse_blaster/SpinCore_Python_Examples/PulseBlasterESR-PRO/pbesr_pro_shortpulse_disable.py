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
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *

clock_freq = 400 # The value of your clock oscillator in MHz

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
            
def input_clock():
    global clock_freq
    while True:
        try:
            clock_freq = float(input("\nPlease enter internal clock frequency (MHz): "))
            break  # Break out of the loop if a valid number is entered
        except ValueError:
            print("Incorrect input. Please enter a valid clock frequency.")
    
    
#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Copyright (c) 2023 SpinCore Technologies, Inc.\n")

print("Using SpinAPI Library version %s" % pb_get_version())

detect_boards() # If there is more than one board in the system, have the user specify. 

if numBoards > 1: # Request the board numbet to use from the user
    select_boards()

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    pause()
    exit(-1)
    
print("Note: Program only works with ESR-PRO boards")
# User input clock
input_clock()

print("\nClock frequency: %1fMHz\n" % clock_freq)
print("All four BNC outputs will output a pulse with a period of 100ns. (50ns on, 50 ns off)")

# Tell driver what clock frequency the board uses
pb_core_clock(clock_freq)

# Disable the short pulse feature
# pb_write_register(REG_SHORTPULSE_DISABLE, 0x1)

# Prepare the board to receive pulse program instructions
pb_start_programming(PULSE_PROGRAM)

# Instruction 0 - Continue to instruction 1 in 50ns
# The lower 4 bits (all BNC connectors) will be driving high
# for 50.0 ns.
start = pb_inst_pbonly(ON | 0xF, CONTINUE, 0, 50.0 * ns)

# Instruction 1 - Branch to "start" (Instruction 0) in 50ns
# Outputs are off
pb_inst_pbonly(0, BRANCH, start, 50.0 * ns)

pb_stop_programming()	# Finished sending instructions

pb_reset()
pb_start()			# Trigger the pulse program

# End communication with the PulseBlasterESR-PRO board. The pulse program
# will continue to run even after this is called.
pb_close()

pause()
