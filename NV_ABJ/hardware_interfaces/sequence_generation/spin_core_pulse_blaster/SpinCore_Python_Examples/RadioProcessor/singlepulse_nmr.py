# Copyright (c) 2023 SpinCore Technologies, Inc.
# http://www.spincore.com
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

##
# singlepulse_nmr.py
# Modified from singlepulse_nmr.c
#
# This program is used to control the RadioProcessor series of boards in conjunction with the iSpin setup.
# It generates a single RF pulse of variable shape, frequency, amplitude, phase and duration.
# It then acquires the NMR response of the perturbing pulse.
#
# SpinCore Technologies, Inc.
# www.spincore.com
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
import math
import ctypes
from singlepulse import *
from singlepulse_user_values import *

def pause():
    
    input("Press enter to continue...")

def processArguments(scanParams):

    # Process arguments
    scanParams.file_name = FILE_NAME

    # Board Parameters
    scanParams.board_num = BOARD_NUMBER
    scanParams.deblank_bit = BLANK_BIT
    scanParams.deblank_bit_mask = (1 << scanParams.deblank_bit)
    scanParams.debug = DEBUG

    # Frequency Parameters
    scanParams.ADC_frequency = ADC_FREQUENCY
    scanParams.SF = SPECTROMETER_FREQUENCY
    scanParams.SW = SPECTRAL_WIDTH

    # Pulse Parameters
    scanParams.enable_tx = ENABLE_TX
    scanParams.use_shape = USE_SHAPE
    scanParams.amplitude = AMPLITUDE
    scanParams.p90_time = PULSE90_TIME
    scanParams.p90_phase = PULSE90_PHASE

    # Acquisition Parameters
    scanParams.enable_rx = ENABLE_RX
    scanParams.bypass_fir = ENABLE_BYPASS_FIR
    scanParams.num_points = roundUpPower2(int(NUMBER_POINTS))  # Only use powers of 2
    scanParams.num_scans = NUMBER_OF_SCANS 

    # Delay Parameters
    scanParams.deblank_delay = BLANKING_DELAY
    scanParams.transient_delay = TRANS_DELAY
    scanParams.repetition_delay = REPETITION_DELAY

    # Ensure number of points is a power of 2
    if scanParams.num_points != int(NUMBER_POINTS):
        print("| Notice:                                                                      |")
        print("|     The desired number of points is not a power of 2.                        |")
        print("|     The number of points have been rounded up to the nearest power of 2.     |")
        print("|                                                                              |")

    # Check if transmit and receive are both disabled and warn user
    if scanParams.enable_tx == 0 and scanParams.enable_rx == 0:
        print("| Notice:                                                                      |")
        print("|     Transmit and receive have both been disabled.                            |")
        print("|     The board will not be programmed.                                        |")
        print("|                                                                              |")

    # Check parameters
    if verifyArguments(scanParams) != 0:
        return INVALID_ARGUMENTS
    else:
        return 0

def verifyArguments(scanParams):
    fw_id = 0
    
    if pb_count_boards() <= 0:
        print("No RadioProcessor boards were detected in your system.")
        return BOARD_NOT_DETECTED
    
    if pb_count_boards() > 0 and scanParams.board_num > (pb_count_boards() - 1):
        print(f"Error: Invalid board number. Use (0-{pb_count_boards() - 1}).")
        return -1
    
    pb_select_board(scanParams.board_num)
    if pb_init():
        print(f"Error initializing board: {pb_get_error()}")
        return -1
    
    fw_id = pb_get_firmware_id()
    if (fw_id > 0xA00 and fw_id < 0xAFF) or (fw_id > 0xF00 and fw_id < 0xFFF):
        if scanParams.num_points > 16*1024 or scanParams.num_points < 1:
            print("Error: Maximum number of points for RadioProcessorPCI is 16384.")
            return -1
    elif fw_id > 0xC00 and fw_id < 0xCFF:
        if scanParams.num_points > 256*1024 or scanParams.num_points < 1:
            print("Error: Maximum number of points for RadioProcessorUSB is 256k.")
            return -1
    
    if scanParams.num_scans < 1:
        print("Error: There must be at least one scan.")
        return -1
    
    if scanParams.p90_time < 0.065:
        print("Error: Pulse time is too small to work with board.")
        return -1
    
    if scanParams.transient_delay < 0.065:
        print("Error: Transient delay is too small to work with board.")
        return -1
    
    if scanParams.repetition_delay <= 0:
        print("Error: Repetition delay is too small.")
        return -1
    
    if scanParams.amplitude < 0.0 or scanParams.amplitude > 1.0:
        print("Error: Amplitude value out of range.")
        return -1
    
    # The RadioProcessor has 4 TTL outputs, check that the blanking bit
    # specified is possible if blanking is enabled.
    if scanParams.deblank_bit < 0 or scanParams.deblank_bit > 3:
        print("Error: Invalid de-blanking bit specified.")
        return -1
    return 0
#
# Terminal Output
#

def printProgramTitle():
    # Create a title block of 80 characters in width
    print("|------------------------------------------------------------------------------|")
    print("|                                                                              |")
    print("|                               Single Pulse NMR                               |")
    print("|                                                                              |")
    print("|                       Using SpinAPI Version:  {:8s}                       |".format(pb_get_version()))
    print("|                                                                              |")
    print("|------------------------------------------------------------------------------|")

def printScanParams(myScan):
    # Create a table of 80 characters in width
    buffer = " " * 80
    print("|-----------------------------  Scan  Parameters  -----------------------------|")
    print("|------------------------------------------------------------------------------|")
    print("| Filename: %-66s |" % myScan.file_name)
    print("|                                                                              |")
    print("| Board Parameters:                                                            |")
    buffer = str(myScan.board_num)
    print("|      Board Number                   : %-38s |" % buffer)
    buffer = str(myScan.deblank_bit)
    print("|      De-blanking TTL Flag Bit       : %-38s |" % buffer)
    print("|      Debugging                      : %-38s |" % ("Enabled" if myScan.debug else "Disabled"))
    print("|                                                                              |")
    print("| Frequency Parameters:                                                        |")
    buffer = "%.4f MHz" % myScan.ADC_frequency
    print("|      ADC Frequency                  : %-38s |" % buffer)
    buffer = "%.4f MHz" % myScan.SF
    print("|      Spectrometer Frequency         : %-38s |" % buffer)
    buffer = "%.4f kHz" % myScan.SW
    print("|      Spectral Width                 : %-38s |" % buffer)
    print("|                                                                              |")
    print("| Pulse Parameters:                                                            |")
    print("|      Enable Transmitter             : %-38s |" % ("Enabled" if myScan.enable_tx else "Disabled"))
    print("|      Use Shape                      : %-38s |" % ("Enabled" if myScan.use_shape else "Disabled"))
    buffer = "%.4f" % myScan.amplitude
    print("|      Amplitude                      : %-38s |" % buffer)
    buffer = "%.4f us" % myScan.p90_time
    print("|      90 Degree Pulse Time           : %-38s |" % buffer)
    buffer = "%.4f degrees" % myScan.p90_phase
    print("|      90 Degree Pulse Phase          : %-38s |" % buffer)
    print("|                                                                              |")
    print("| Acquisition Parameters:                                                      |")
    print("|      Enable Reciever                : %-38s |" % ("Enabled" if myScan.enable_rx else "Disabled"))
    print("|      Bypass FIR                     : %-38s |" % ("Enabled" if myScan.bypass_fir else "Disabled"))
    buffer = str(myScan.num_points)
    print("|      Number of Points               : %-38s |" % buffer)
    buffer = str(myScan.num_scans)
    print("|      Number of Scans                : %-38s |" % buffer)
    buffer = "%.4f ms" % myScan.scan_time
    print("|      Total Acquisition Time         : %-38s |" % buffer)
    print("|                                                                              |")
    print("| Delay Parameters:                                                            |")
    buffer = "%.4f ms" % myScan.deblank_delay
    print("|      De-blanking Delay              : %-38s |" % buffer)
    buffer = "%.4f us" % myScan.transient_delay
    print("|      Transient Delay                : %-38s |" % buffer)
    buffer = "%.4f s" % myScan.repetition_delay
    print("|      Repetition Delay               : %-38s |" % buffer)
    print("|                                                                              |")
    print("|------------------------------------------------------------------------------|")

def configureBoard(myScan):
    
    pb_set_defaults()
    pb_core_clock(myScan.ADC_frequency)
    
    pb_overflow(1, 0)   # Reset the overflow counters
    pb_scan_count(1)    # Reset scan counter
    
    # Load the shape parameters
    shape_data = [0]*1024
    num_lobes = 3
    
    make_shape_data(shape_data, num_lobes, shape_sinc)
    pb_dds_load(shape_data, DEVICE_SHAPE)
    pb_set_amp(myScan.amplitude if myScan.enable_tx else 0, 0)
    
    
    ###
    ### Set acquisition parameters
    ###
    
    # Determine actual spectral width
    cmd = 0
    if myScan.bypass_fir:
        cmd = BYPASS_FIR

    SW_MHz = myScan.SW / 1000.0

    dec_amount = pb_setup_filters(SW_MHz, myScan.num_scans, cmd)
    
    if dec_amount <= 0:
        print("\n\nError: Invalid data returned from pb_setup_filters(). Please check your board.\n")
        return INVALID_DATA_FROM_BOARD

    ADC_frequency_kHz = myScan.ADC_frequency * 1000
    myScan.actual_SW = ADC_frequency_kHz / float(dec_amount)
    
 
    # Determine scan time, the total amount of time that data is collected in one scan cycle
    myScan.scan_time = (float(myScan.num_points) / (myScan.actual_SW))
    
    
    pb_set_num_points(myScan.num_points)
    pb_set_scan_segments(1)
    
    return 0

def programBoard(myScan):
    if not myScan.enable_rx and not myScan.enable_tx:
        return RX_AND_TX_DISABLED
    
    scan_loop_label = None
    
    # Program frequency, phase and amplitude registers
    
    # Frequency
    pb_start_programming(FREQ_REGS)
    pb_set_freq(myScan.SF * MHz)
    pb_set_freq(checkUndersampling(myScan))
    pb_stop_programming()
    
    # Real Phase
    pb_start_programming(COS_PHASE_REGS)
    pb_set_phase(0.0)
    pb_set_phase(90.0)
    pb_set_phase(180.0)
    pb_set_phase(270.0)
    pb_stop_programming()
    
    # Imaginary Phase
    pb_start_programming(SIN_PHASE_REGS)
    pb_set_phase(0.0)
    pb_set_phase(90.0)
    pb_set_phase(180.0)
    pb_set_phase(270.0)
    pb_stop_programming()
    
    # Transmitted Phase
    pb_start_programming(TX_PHASE_REGS)
    pb_set_phase(myScan.p90_phase)
    pb_stop_programming()
    
    # Amplitude
    pb_set_amp(myScan.amplitude, 0)
    
    # Specify pulse program
    pb_start_programming(PULSE_PROGRAM)
    
    scan_loop_label = (
        # De-blank amplifier for the blanking delay so that it can fully amplify a pulse
        # Initialize scan loop to loop for the specified number of scans
        # Reset phase so that the excitation pulse phase will be the same for every scan
        pb_inst_radio_shape(0, PHASE090, PHASE000, 0, TX_DISABLE, PHASE_RESET, 
            NO_TRIGGER, 0, 0, myScan.deblank_bit_mask, LOOP, myScan.num_scans, myScan.deblank_delay * ms)
    )
    
    # Transmit 90 degree pulse
    pb_inst_radio_shape(0, PHASE090, PHASE000, 0, myScan.enable_tx, NO_PHASE_RESET, 
        NO_TRIGGER, myScan.use_shape, 0, myScan.deblank_bit_mask, CONTINUE, 0, myScan.p90_time * us)
    
    # Wait for the transient to subside
    pb_inst_radio_shape(0, PHASE090, PHASE000, 0, TX_DISABLE, NO_PHASE_RESET, 
        NO_TRIGGER, 0, 0, BLANK_PA, CONTINUE, 0, myScan.transient_delay * us)
    
    # Trigger acquisition
    pb_inst_radio_shape(1, PHASE090, PHASE000, 0, TX_DISABLE, NO_PHASE_RESET, 
        myScan.enable_rx, 0, 0, BLANK_PA, CONTINUE, 0, myScan.scan_time * ms)
    
    # Allow sample to relax before performing another scan cycle
    pb_inst_radio_shape(0, PHASE090, PHASE000, 0, TX_DISABLE, NO_PHASE_RESET, 
        NO_TRIGGER, 0, 0, BLANK_PA, END_LOOP, scan_loop_label, myScan.repetition_delay * 1000.0 * ms)
    
    # After all scans complete, stop the pulse program
    pb_inst_radio_shape(0, PHASE090, PHASE000, 0, TX_DISABLE, NO_PHASE_RESET, 
        NO_TRIGGER, 0, 0, BLANK_PA, STOP, 0, 1.0 * us)
    
    pb_stop_programming()
    
    return 0
    
#
# \file Writing
#

def createFelixTitleBlock(myScan, title_string):
    # These variables are used for the Title Block in Felix
    program_type = "singlepulse_nmr"
    buff_string = ""

    # Create Title Block String
    title_string += "Program = "
    title_string += program_type
    title_string += "\r\n\r\n90 Degree Pulse Time = "
    buff_string = str(myScan.p90_time)
    title_string += buff_string
    title_string += "\r\nTransient Delay = "
    buff_string = str(myScan.transient_delay)
    title_string += buff_string
    title_string += "\r\nRepetition Delay = "
    buff_string = str(myScan.repetition_delay)
    title_string += buff_string
    title_string += "\r\n# of Scans = "
    buff_string = str(myScan.num_scans)
    title_string += buff_string
    title_string += "\r\nADC Freq = "
    buff_string = str(myScan.ADC_frequency)
    title_string += buff_string
    title_string += "\r\nAmplitude = "
    buff_string = str(myScan.amplitude)
    title_string += buff_string
    title_string += "\r\nEnable TX = "
    buff_string = str(int(myScan.enable_tx))
    title_string += buff_string
    title_string += "\r\nEnable RX = "
    buff_string = str(int(myScan.enable_rx))
    title_string += buff_string
    title_string += "\r\nBlanking Bit = "
    buff_string = str(myScan.deblank_bit)
    title_string += buff_string
    title_string += "\r\nDe-blanking Delay = "
    buff_string = str(myScan.deblank_delay)
    title_string += buff_string
    title_string += "\r\n# of Points = "
    buff_string = str(myScan.num_points)
    title_string += buff_string
    title_string += "\r\nSpectral Width = "
    buff_string = str(myScan.SW)
    title_string += buff_string
    title_string += "\r\nSpectrometer Freq = "
    buff_string = str(myScan.SF)
    title_string += buff_string
    title_string += "\r\nBypass FIR = "
    buff_string = str(myScan.bypass_fir)
    title_string += buff_string
    title_string += "\r\nUse Shape = "
    buff_string = str(myScan.use_shape)
    title_string += buff_string

def writeDataToFiles(myScan, real, imag):
    actual_SW_Hz = myScan.actual_SW * 1000

    # Set up file names		
	# Copy up to 5 less than the file name size to leave room for extension and null terminator
    fid_fname = myScan.file_name[:FNAME_SIZE-5] + ".fid"
    jcamp_fname = myScan.file_name[:FNAME_SIZE-5] + ".jdx"
    ascii_fname = myScan.file_name[:FNAME_SIZE-5] + ".txt"

    Felix_title_block = ""

    createFelixTitleBlock(myScan, Felix_title_block)

    pb_write_felix(fid_fname, Felix_title_block, myScan.num_points,
                   actual_SW_Hz,
                   myScan.SF, real, imag)
    pb_write_ascii_verbose(ascii_fname, myScan.num_points,
                            actual_SW_Hz,
                            myScan.SF, real, imag)
    pb_write_jcamp(jcamp_fname, myScan.num_points,
                   actual_SW_Hz,
                   myScan.SF, real, imag)

#
# Calculations
#

def make_shape_data(shape_array, arg, shapefnc):
    shapefnc(shape_array, arg)

def shape_sinc(shape_data, nlobe):
    pi = 3.1415926
    lobes = nlobe
    x = 0.0
    scale = lobes * (2.0 * pi)
    
    for i in range(1024):
        x = (i - 512) * scale / 1024.0
        if x == 0.0:
            shape_data[i] = 1.0
        else:
            shape_data[i] = math.sin(x) / x

def checkUndersampling(myScan):
    folding_constant = 0
    folded_frequency = 0.0
    adc_frequency = myScan.ADC_frequency
    spectrometer_frequency = myScan.SF
    nyquist_frequency = adc_frequency / 2.0
    
    if spectrometer_frequency > nyquist_frequency:
        if (spectrometer_frequency / adc_frequency - math.floor(spectrometer_frequency / adc_frequency)) >= 0.5:
            folding_constant = math.ceil(spectrometer_frequency / adc_frequency)
        else:
            folding_constant = math.floor(spectrometer_frequency / adc_frequency)
        
        folded_frequency = abs(spectrometer_frequency - folding_constant * adc_frequency)
        
        print(f"Undersampling Detected: Spectrometer Frequency ({spectrometer_frequency:.4f} MHz) is greater than Nyquist ({nyquist_frequency:.4f} MHz).\n")
        
        spectrometer_frequency = folded_frequency
        
        print(f"Using Spectrometer Frequency: {spectrometer_frequency} MHz.\n")
    
    return spectrometer_frequency

# Round a number up to the nearest power of 2
def roundUpPower2(number):
    remainder_total = 0
    rounded_number = 1
    
    # Determine next highest power of 2
    while number != 0:
        remainder_total += number % 2
        number //= 2
        rounded_number *= 2
    
    # If the number was originally a power of 2, it will only have a remainder for 1/2, which is 1
    # Then lower it a power of 2 to receive the original value
    if remainder_total == 1:
        rounded_number //= 2
    
    return rounded_number


# Main
myScan = SCANPARAMS

printProgramTitle()

# Process Arguments

if processArguments(myScan) != 0:
    pause()
    exit(-1)
    
real = (ctypes.c_int * myScan.num_points)()
imag = (ctypes.c_int * myScan.num_points)()

if myScan.debug == 1:
    pb_set_debug(1)

# Configure Board
if configureBoard(myScan) < 0:
    print("Error: Failed to configure board.")
    pause()
    exit(-1)

# Print Parameters
printScanParams(myScan)

# Calculate and print total time
repetition_delay_ms = myScan.repetition_delay * 1000
total_time = (myScan.scan_time + repetition_delay_ms) * myScan.num_scans
if total_time < 1000:
    print(f"Total Experiment Time   : {total_time:1f} ms\n")
elif total_time < 60000:
    print(f"Total Experiment Time   : {total_time/1000:1f} s\n")
elif total_time < 3600000:
    print(f"Total Experiment Time   : {total_time/60000:1f} minutes\n")
else:
    print(f"Total Experiment Time   : {total_time/3600000:1f} hours\n")
print("\nWaiting for the data acquisition to complete... \n")


# Program Board

if programBoard(myScan) != 0:
    print("Error: Failed to program board.")
    pause()
    exit(-1) # PROGRAMMING_FAILED

# Trigger Pulse Program

pb_reset()
pb_start()

# Count Scans

scan_count = 0  # Scan count is not deterministic. Reported scans may be skipped or repeated (actual scan count is correct)
while not (pb_read_status() & STATUS_STOPPED):
    pb_sleep_ms(int(total_time/myScan.num_scans))
    
    if scan_count != pb_scan_count(0):
        scan_count = pb_scan_count(0)
        print("Current Scan:", scan_count)

print("\nExecution complete \n\n")

# Read Data From RAM

if myScan.enable_rx:

    if pb_get_data(myScan.num_points, real, imag) < 0:
        print("Failed to get data from board.")
        pause()
        exit(-1) # DATA_RETRIEVAL_FAILED

    # Estimate resonance frequency
    SF_Hz = myScan.SF * 1e6
    actual_SW_Hz = myScan.SW * 1e3
    myScan.res_frequency = pb_fft_find_resonance(myScan.num_points, SF_Hz, actual_SW_Hz, real, imag) / 1e6

    # Print resonance estimate
    print("Highest Peak Frequency: %f MHz\n\n" % myScan.res_frequency)

    #
    # Write Output Files
    #

    writeDataToFiles(myScan, real, imag)


# End Program

pb_stop()
pb_close()

del myScan
del real
del imag