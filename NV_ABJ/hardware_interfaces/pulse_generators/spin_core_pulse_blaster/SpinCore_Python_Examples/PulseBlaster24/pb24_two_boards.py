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
# \file pb24_two_boards.py
# This program demonstrates the use of two boards: board 0 (first board) and 
# board 1 (second board).
# The user will see the following on board 0's digital output 0:
#  -On for 1 ms
#  -Off for 2 ms
# 
# And the following on board 1's digital output 1:
#  -On for 3 ms
#  -Off for 4 ms
# Both programs loop continously until termination
# The boards are programmed one after the other and then started one right
# after the other. Upon button press both boards are stopped and closed one
# right after the other
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

# Core clock frequency of board 0
CLOCK_FREQ0 = 100.0
# Core clock frequency of board 1
CLOCK_FREQ1 = 100.0

def pause():
    input("Press enter to continue...")


#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Copyright (c) 2023 SpinCore Technologies, Inc.\n")

print("Using SpinAPI Library version %s\n" % pb_get_version())

numBoards = pb_count_boards()
if numBoards < 2:
    print("This example requires two boards attached to the system.")
    pause()
    exit(-1)

# Select board 0 for programming
pb_select_board(0)

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    pause()
    exit(-1)

print("Digital output 0 on the first board will output a "
      "pattern of on for 1 ms and off for 2 ms, assuming a core clock "
      "frequency of %0.1f MHz.\n" % CLOCK_FREQ0)

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(CLOCK_FREQ0)

pb_start_programming(PULSE_PROGRAM)

# Instruction 0 - Continue to instruction 1 in 100ms
# Flags = 0x1, OPCODE = CONTINUE
start = pb_inst_pbonly(0x1, CONTINUE, 0, 1.0 * ms)

# Instruction 1 - Continue to instruction 2 in 100ms
# Flags = 0x0, OPCODE = CONTINUE
pb_inst_pbonly(0x0, CONTINUE, 0, 1.0 * ms)

# Instruction 2 - Branch to "start" (Instruction 0) in 100ms
# 0x0, OPCODE = BRANCH, Target = start
pb_inst_pbonly(0x0, BRANCH, start, 1.0 * ms)

# End of programming board 0
pb_stop_programming()

# Second Program to run on other board, simple test

# Select second board
pb_select_board(1)

if pb_init() != 0:
	print("Error initializing board: %s" % pb_get_error())
	pause()
	exit(-1)
    
print("Digital output 1 on the second board will output a "
	  "pattern of on for 3 ms and off for 4 ms, assuming a core clock "
	  "frequency of %0.1f MHz.\n" % CLOCK_FREQ1) 

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(CLOCK_FREQ1)

pb_start_programming(PULSE_PROGRAM)
   
# Instruction 0 - Continue to instruction 1 in 100ms
# Flags = 0x2, OPCODE = CONTINUE
start = pb_inst_pbonly(0x2, CONTINUE, 0, 3.0 * ms)
   
# Instruction 1 - Continue to instruction 2 in 100ms
# Flags = 0x0, OPCODE = CONTINUE
pb_inst_pbonly(0x0, CONTINUE, 0, 2.0 * ms)
   
# Instruction 2 - Branch to "start" (Instruction 0) in 100ms
# 0x0, OPCODE = BRANCH, Target = start
pb_inst_pbonly(0x0, BRANCH, start, 2.0 * ms)

pb_stop_programming()

# Trigger the first program
pb_select_board(0)
pb_start()

# Trigger the second program
pb_select_board(1)
pb_start()

pause()

#Stop and Close both boards in sequence
pb_select_board(0)
pb_stop()
pb_close()

pb_select_board(1)
pb_stop()
pb_close()
