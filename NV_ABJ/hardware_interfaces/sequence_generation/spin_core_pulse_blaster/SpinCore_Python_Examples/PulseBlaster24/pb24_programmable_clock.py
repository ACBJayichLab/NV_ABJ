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
# \file pb24_programmable_clock.py
# PulseBlaster24 Programmable Clock Example
#
# \brief This program demonstrates use of the user programmable clock outputs.
# This program will only work with firmware 13-9.  Other firmwares do not have
# this custom behavior.  This example generates a clock signal with a 5 MHz
# frequency and a 10% duty cycle on the four clock pins.  Each clock pin will
# be offset by a different amount.  For more details, see Appendix II of the
# PulseBlaster USB manual.
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

print("This example program will generate a clock signal of 5 MHz and a 10% duty cycle for the PulseBlaster.\n")

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
        choice = int(input(f"Found {numBoards} boards in your system. Which board should be used? (0-{numBoards-1}): "))
        
        if choice < 0 or choice >= numBoards:
            print("Invalid Board Number (%d)." % choice)
        else:
            pb_select_board(choice)
            print("Board %d selected." % choice)
            break;
                 

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

# check to see if the firmware is 13-09
firmware = pb_get_firmware_id()
if firmware != 0x0D09:
    print("Error: This program only works with firmware 13-9.")
    print("This example does not apply to your board.")
    pause()
    exit(-1)
    
print("Clock frequency: 100.00MHz\n")

print("User Programmable Clock Example Program")
print("Only works with USB PulseBlaster firmware 13-9.\n")
print("This example generates a clock signal with a 5 MHz frequency")
print(" and a 10%% duty cycle on the four clock pins.  Each clock pin")
print(" will be offset by a different amount.\n")

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(100.0)
	
# Channel 0 - 200 ns period - 20 ns high - 20 ns offset
pb_set_pulse_regs(0, 200.0 * ns, 20.0 * ns, 20.0 * ns)
	
# Channel 1 - 200 ns period - 20 ns high - 20 ns offset
pb_set_pulse_regs(1, 200.0 * ns, 20.0 * ns, 40.0 * ns)
	
# Channel 2 - 200 ns period - 20 ns high - 20 ns offset
pb_set_pulse_regs(2, 200.0 * ns, 20.0 * ns, 60.0 * ns)
	
# Channel 3 - 200 ns period - 20 ns high - 20 ns offset
pb_set_pulse_regs(3, 200.0 * ns, 20.0 * ns, 80.0 * ns)

print("The clock pins should now be running.")
	
pause()

pb_close()

