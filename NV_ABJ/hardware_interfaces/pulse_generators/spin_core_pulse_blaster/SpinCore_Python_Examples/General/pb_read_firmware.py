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
# \file read_firmware.py
# \brief This example program will print the firmware(s) of detected device(s).
# \ingroup genex
#

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *

FW_DEV_MSK = 0xFF00
FW_REV_MSK = 0x00FF

def pause():
    input("Press enter to continue...")

#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Copyright (c) 2023 SpinCore Technologies, Inc.\n")

print("Using SpinAPI Library version %s" % pb_get_version())

numBoards = pb_count_boards()
print("Detected %d Boards." % numBoards)

for i in range(numBoards):
    pb_select_board(i)  # Select the ith board 
    
    if pb_init() != 0:
        print("Error initializing board: %s" % pb_get_error())
        pause()
        exit(-1)
    
    fw = pb_get_firmware_id()
    device = (fw & FW_DEV_MSK) >> 8 # Get device number from ID 
    revision = (fw & FW_REV_MSK) # Get revision number from ID
    
    print("Board %d Firmware ID: %d-%d" % (i, device, revision))
    
    pb_close()

    
print("\n")
pause()
