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
# 1. The origin of this software must not be misrepresented you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

##
# \file pb24_ex4.py
# PulseBlaster24 Example 4
#
# \brief This program demonstrates use of the WAIT op code.
# This program will generate ten pulses 100ms long (50% duty cycle) on all TTL
# outputs and then wait for the hardware trigger. Upon triggering, the board
# will  wait 100ms then repeat the pulse pattern and wait for another trigger.
# This behavior will repeat until pb_stop is called.
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

print("Clock frequency: %1fMHz\n" %clock)
print("All outputs should turn on and then off 10 times with a 100ms "
      "period and 50% duty cycle. The board will then wait for a "
      "hardware trigger signal before repeating.")

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(clock)

pb_start_programming(PULSE_PROGRAM)

# Instruction 0 - Loop 10 times, instruction delays 50ms.
# Flags = 0xFFFFFF, OPCODE = LOOP
start = pb_inst_pbonly(0xFFFFFF, LOOP, 10, 50.0 * ms)

# Instruction 1 - End the loop, delay 50ms.
# Flags = 0x000000, OPCODE = END_LOOP
pb_inst_pbonly(0x0, END_LOOP, start, 50.0 * ms)

# Instruction 2 - Wait for a hardware trigger.
# Flags = 0x000000, OPCODE = WAIT
pb_inst_pbonly(0x0, WAIT, 0, 50.0 * ms)

# Instruction 3 - Branch back to the beginning of the program.
# Flags = 0x000000, OPCODE = BRANCH
pb_inst_pbonly(0x0, BRANCH, start, 50.0 * ms)

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
