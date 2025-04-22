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
# \file pbesr_pro_long_delay_test.py
# \brief PulseBlasterESR-PRO example program
#  
#  The following program tests the functionality of the long delay opcode. The
#  long delay opcode determines what the delay value is by multipling the given
#  delay value by the data field. Thus, this program will output a pulse train
#  with period (100ns*long_delay)
#  
#  This program takes two optional command-line arguments.
#  The first is the clock frequency, the default is 400MHz.  
#  The second is the number of delay loops in the pulse train, the default is 5.  
#  
#  The largest value for the delay field of pb_inst is 850ns.
#  For longer delays, use the LONG_DELAY instruction.  The maximum value
#  for the data field of the LONG_DELAY is 1048576.  Even longer delays can
#  be achieved using the LONG_DELAY instruction inside of a loop.
#
#  \ingroup ESRPRO
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

clock_freq = 500.0 #The value of your clock oscillator in MHz
delay_loop = 5

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

# If there is more than one board in the system, have the user specify. 
detect_boards()

if numBoards > 1:
    select_boards()

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
            print("Please enter the number of loops for the long delay instruction.\n"
                   "The minimum number of loops for this program to run is 3.\n"
                   "The resulting period will be 200*(number of loops)ns.")
            delay_loop = int(input("Number of long delay loops: "))
            while delay_loop < 3:
                print("The number of loops has to be greater that 2.")
                delay_loop = int(input("Number of long delay loops: "))
            break
        except ValueError:
            print("\nIncorrect input. Please enter a valid number of loops.\n")

print("\nClock frequency: %.2fMHz\n" % clock_freq)
print("BNCs 0-3 should output a 50%% duty cycle square wave with period %dns\n" % (delay_loop * 100 * 2));

# Tell driver what clock frequency the board uses
pb_core_clock(clock_freq)

# Begin pulse program
pb_start_programming(PULSE_PROGRAM)

# Instruction format
# int pb_inst_pbonly(int flags, int inst, int inst_data, int length)

# Instruction 0 - continue to inst 1 in (100ns*delay_loop)
start = pb_inst_pbonly(ON | 0xF, LONG_DELAY, delay_loop, 100.0 * ns)

# Instruction 1 - continue to instruction 2 in (100ns*(delay_loop-1))
pb_inst_pbonly(0x0, LONG_DELAY, delay_loop - 1, 100.0 * ns)

# Instruction 2 - branch to start
pb_inst_pbonly(0x0, BRANCH, start, 100.0 * ns)

# End of programming registers and pulse program
pb_stop_programming()

# Trigger pulse program
pb_reset()
pb_start()

pb_close()

pause()
