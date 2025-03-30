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
# \file pbesr_pro_loop_test.py
# \brief PulseBlasterESR-PRO example program
# 
# The following program tests the functionality of the loop instruction.
# It takes two optional command-line arguments.
# The first is the clock frequency, the default is 400MHz.  
# The second is the number of loops, the default is 3 loops.  
#  
# BNCs 0-3 will output a pulse train with period 100ns. The number of pulses
# in this train will be determined by the number of loops used. This pulse
# train will be followed by ground level for 400ns, after which the entire
# program will repeat.
# 
# \ingroup ESRPRO
#  

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *
import sys

clock_freq = 400.0	#The value of your clock oscillator in MHz
num_loops = 3

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

detect_boards() 

if numBoards > 1: # If there is more than one board in the system, have the user specify. 
    select_boards() # Request the board numbet to use from the user

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    pause()
    exit(-1)

# Set the clock frequency.
argc = len(sys.argv)
if argc > 1:
    try: 
        clock_freq = float(sys.argv[1])
    except Exception as e:
        print(f"\n{e}, clock frequency set to {clock_freq} MHz")
else: 
    # User input clock
    input_clock()
    print("\n")

if argc > 2:
    try: 
        num_loops = int(sys.argv[2])
    except Exception as e:
        print(f"\n{e}, num_loops set to {num_loops}")
else:
    while True:
        try:
            print("Please enter the number of loops for the loop instruction. ")
            num_loops = int(input("Number of loops: "))
            break
        except ValueError:
            print("Incorrect input. Please enter a valid number of loops.")

print("\nClock frequency: %.2fMHz\n" % clock_freq)
print("BNCs 0-3 will output %d successive pulses, each with a period of 100ns, followed by ground level for 400ns and then the program will repeat\n\n" % num_loops)

# Tell driver what clock frequency the board uses
pb_core_clock(clock_freq)

# Begin pulse program
pb_start_programming(PULSE_PROGRAM)

# Instruction format
# int pb_inst_pbonly(int flags, int inst, int inst_data, int length)

# Instruction 0 - continue to inst 1 in 200ns
start = pb_inst_pbonly(0x0, CONTINUE, 0, 200.0 * ns);

# Instruction 1 - Beginning of Loop (Loop num_loop times). Continue to
# next instruction in 50ns
loop = pb_inst_pbonly(ON | 0xF, LOOP, num_loops, 50.0 * ns);

# Instruction 2 - End of Loop.  Return to beginning of loop (instruction 1)
# or continue to next instruction in 50ns
pb_inst_pbonly(0x0, END_LOOP, loop, 50.0 * ns);

# Instruction 3 - branch to start
pb_inst_pbonly(0x0, BRANCH, start, 200.0 * ns);

# End of programming registers and pulse program
pb_stop_programming()

# Trigger pulse program
pb_reset()
pb_start()

pb_close()

pause()
