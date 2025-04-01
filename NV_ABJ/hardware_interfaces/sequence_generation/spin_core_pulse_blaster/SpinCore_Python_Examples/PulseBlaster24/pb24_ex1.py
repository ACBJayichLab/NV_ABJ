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

##
# \file pb24_ex1.py
# PulseBlaster24 Example 1
#
# \brief This program will cause the outputs to turn on and off with a period of 4
#       400ms.
# \ingroup pb24
#

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
            
def input_clock():
    global clock
    while True:
        try:
            clock = float(input("\nPlease enter internal clock frequency (MHz): "))
            break  # Break out of the loop if a valid number is entered
        except ValueError:
            print("Incorrect input. Please enter a valid clock frequency.")


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


# User input clock
input_clock()

print("\nClock frequency: %1fMHz\n" %clock)
print("All outputs should now be turning on and off with a period of"
      " 400ms and \n50 percent duty cycle.\n")

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(clock)

pb_start_programming(PULSE_PROGRAM)

# Instruction 0 - Continue to instruction 1 in 200ms
# Flags = 0xFFFFFF, OPCODE = CONTINUE
start = pb_inst_pbonly(0xFFFFFF, CONTINUE, 0, 200.0 * ms)

# Instruction 1 - Continue to instruction 2 in 100ms
# Flags = 0x0, OPCODE = CONTINUE
pb_inst_pbonly(0x0, CONTINUE, 0, 100.0 * ms);

# Instruction 2 - Branch to "start" (Instruction 0) in 100ms
# 0x0, OPCODE = BRANCH, Target = start
pb_inst_pbonly(0x0, BRANCH, start, 100.0 * ms)

pb_stop_programming()

# Trigger the pulse program
pb_reset()
pb_start()

# Read the status register
status = pb_read_status()
print("status: %d " % status)
print(pb_status_message())

pause()

pb_stop()
pb_close()
