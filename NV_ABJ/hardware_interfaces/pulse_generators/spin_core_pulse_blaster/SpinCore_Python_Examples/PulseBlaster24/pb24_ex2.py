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
# \file pb24_ex2.py
# PulseBlaster24 Example 2
#
# \brief This example makes use of all instructions (except WAIT).
# The user will see:
# -the outputs on for 1.0 second
# -the outputs off for 0.5 seconds
# -half of the outputs (0xF0F0F0) on for 0.5 seconds
# -the outputs turning off and on three times with a period of 0.3 seconds 
# -the outputs off for 1.5 seconds
#
# This program loops back to the begining when it finishes.
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

print("Clock frequency: %1fMHz\n" % clock)
print("The outputs should now be repeating the following pattern:\n")
print("-on for 1.0 second")
print("-off for 0.5 seconds")
print("-half (0xF0F0F0) on for 0.5 seconds")
print("-off and on three times with a period of 0.3 seconds")
print("-off for 1.5 seconds\n")

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(clock)

pb_start_programming(PULSE_PROGRAM)

# Since we are going to jump forward in our program, we need to 
# define this variable by hand.  Instructions start at 0 and count up
sub = 5

# Instruction format
# int pb_inst(int flags, int inst, int inst_data, int length)

# Instruction 0 - Jump to Subroutine at Instruction 5 in 1s
start = pb_inst_pbonly(0xFFFFFF, JSR, sub, 1000.0 * ms)

# Loop. Instructions 1 and 2 will be repeated 3 times
# Instruction 1 - Beginning of Loop (Loop 3 times).  Continue to next
# instruction in 1s
loop = pb_inst_pbonly(0x0, LOOP, 3, 150.0 * ms)
# Instruction 2 - End of Loop.  Return to beginning of loop or continue
# to next instruction in .5 s
pb_inst_pbonly(0xFFFFFF, END_LOOP, loop, 150.0 * ms)

# Instruction 3 - Stay here for (5*100ms) then continue to Instruction 4
pb_inst_pbonly(0x0, LONG_DELAY, 5, 100.0 * ms)

# Instruction 4 - Branch to "start" (Instruction 0) in 1 s
pb_inst_pbonly(0x0, BRANCH, start, 1000.0 * ms)

# Subroutine
# Instruction 5 - Continue to next instruction in 1 * s
pb_inst_pbonly(0x0, CONTINUE, 0, 500.0 * ms)
# Instruction 6 - Return from Subroutine to Instruction 1 in .5*s
pb_inst_pbonly(0xF0F0F0, RTS, 0, 500.0 * ms)

# End of pulse program
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
