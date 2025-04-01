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
# CYCLOPS_nmr.c
# This program is used to control the RadioProcessor series of boards.
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
import math
import ctypes
from CYCLOPS import *
from CYCLOPS_user_values import *
title_string = ""

def pause():
    input("Press enter to continue...")
    
def processArguments(SCANPARAMS, CYCLOPSPARAMS):

    scanParams = SCANPARAMS
    cyclopsParams = CYCLOPSPARAMS
    scanParams.board_num = BOARD_NUMBER
    scanParams.nPoints = NUMBER_POINTS
    scanParams.spectrometerFrequency = SPECTROMETER_FREQUENCY
    scanParams.spectralWidth = SPECTRAL_WIDTH
    scanParams.pulseTime = PULSE_TIME
    scanParams.transTime = TRANS_TIME
    scanParams.repetitionDelay = REPETITION_DELAY
    scanParams.nScans = NUMBER_OF_SCANS
    scanParams.tx_phase = TX_PHASE
    scanParams.outputFilename = FNAME
    scanParams.bypass_fir = BYPASSFIR
    scanParams.adcFrequency = ADC_FREQUENCY
    scanParams.use_shape = SHAPED_PULSE
    scanParams.amplitude = AMPLITUDE
    scanParams.enable_tx = ENABLE_TX
    scanParams.enable_rx = ENABLE_RX
    scanParams.verbose = VERBOSE
    scanParams.blankingEnable = BLANKING_EN
    scanParams.blankingBit = BLANKING_BITS
    scanParams.blankingDelay = BLANKING_DELAY
    
    cyclopsParams.add_sub_re_0 = REAL_ADD_SUB_0
    cyclopsParams.add_sub_im_0 = IMAG_ADD_SUB_0
    cyclopsParams.swap_0 = SWAP_0
    cyclopsParams.add_sub_re_1 = REAL_ADD_SUB_1
    cyclopsParams.add_sub_im_1 = IMAG_ADD_SUB_1
    cyclopsParams.swap_1 = SWAP_1
    cyclopsParams.add_sub_re_2 = REAL_ADD_SUB_2
    cyclopsParams.add_sub_im_2 = IMAG_ADD_SUB_2
    cyclopsParams.swap_2 = SWAP_2
    cyclopsParams.add_sub_re_3 = REAL_ADD_SUB_3
    cyclopsParams.add_sub_im_3 = IMAG_ADD_SUB_3
    cyclopsParams.swap_3 = SWAP_3
    scanParams.debug = DEBUG
     
    if verifyArguments(scanParams, scanParams.verbose) != 0:
        return INVALID_ARGUMENTS
    else:
        return 0
        
def verifyArguments(scanParams, verbose):
    
    if pb_count_boards() <= 0:
        print("No RadioProcessor boards were detected in your system.")
        return BOARD_NOT_DETECTED
    
    if pb_count_boards() > 0 and scanParams.board_num > pb_count_boards() - 1:
        if verbose:
            print("Error: Invalid board number. Use (0-%d)." % (pb_count_boards()-1))
        return -1

    pb_select_board(scanParams.board_num)
    
    if pb_init():
        print("Error initializing board: %s" % pb_get_error)
        return -1

    fw_id = pb_get_firmware_id()
    if (fw_id > 0xA00 and fw_id < 0xAFF) or (fw_id > 0xF00 and fw_id < 0xFFF):
        if scanParams.nPoints > 16 * 1024 or scanParams.nPoints < 1:
            if verbose:
                print("Error: Maximum number of points for RadioProcessorPCI is 16384.")
            return -1
            
    elif fw_id > 0xC00 and fw_id < 0xCFF:
        if scanParams.nPoints > 256*1024 or scanParams.nPoints < 1:
            if verbose:
                print("Error: Maximum number of points for RadioProcessorUSB is 256k.")
            return -1
    
    if scanParams.nScans < 1:
        if verbose:
            print("Error: There must be at least one scan.")
        return -1
        
    elif scanParams.nScans%4!=0 and scanParams.nScans!=1:
        if verbose:
            print("Error: To run CYCLOPS with multiple scans, the Number of Scans must be a multiple of 4.")
        return -1
    
    if scanParams.pulseTime < 0.065:
        if verbose:
            print("Error: Pulse time is too small to work with board.")
        return -1
    
    if scanParams.transTime < 0.065:
        if verbose:
            print("Error: Transient time is too small to work with board.")
        return -1
    
    if scanParams.amplitude < 0.0 or scanParams.amplitude > 1.0:
        if verbose:
            print("Error: Amplitude value out of range.")
        return -1
    return 0
    
def outputScanParams(myScan):
    print("Filename                : %s" % myScan.outputFilename)
    print("Board Number            : %d" % myScan.board_num)
    print("Number of Points        : %d" % myScan.nPoints)
    print("Number of Scans         : %d" % myScan.nScans)
    print("Use shape               : %d" % myScan.use_shape)
    print("Bypass FIR              : %d" % myScan.bypass_fir)
    print("Amplitude               : %f" % myScan.amplitude)
    print("Spectrometer Frequency  : %f MHz" % myScan.spectrometerFrequency)
    print("Spectral Width          : %f kHz" % myScan.spectralWidth)
    print("TX Phase                : %f degrees" % myScan.tx_phase)
    print("Pulse Time              : %f us" % myScan.pulseTime)
    print("Trans Time              : %f us" % myScan.transTime)
    print("Repetition Delay        : %f s" % myScan.repetitionDelay)
    print("ADC Frequency           : %f MHz" % myScan.adcFrequency)
    print("Enable Transmitter      : %d" % myScan.enable_tx)
    print("Enable Receiver         : %d" % myScan.enable_rx)
    print("Use TTL Blanking        : %d" % myScan.blankingEnable)
    print("Blanking TTL Flag Bits  : 0x%x" % myScan.blankingBit)
    print("Blanking Delay          : %f ms" % myScan.blankingDelay)
    print("Debugging               : %s" % ("Enabled" if myScan.debug != 0 else "Disabled"))

def make_shape_data(shape_array, arg, shapefnc):
    shapefnc(shape_array, arg)
    
def shape_sinc(shape_data, nlobe):
    pi = 3.1415926
    lobes = nlobe
    scale = lobes * (2.0 * pi)

    for i in range(1024):
        x = (i - 512) * scale / 1024.0
        if x == 0.0:
            shape_data[i] = 1.0
        else:
            shape_data[i] = math.sin(x) / x
            
def configureBoard(myScan):
    
    shape_data = [0.0] * 1024
    
    actual_SW = 0.0
    wait_time = 0.0
    spectralWidth_MHZ = myScan.spectralWidth / 1000.0

    dec_amount = 0
    num_lobes = 3
    cmd = 0

    pb_set_defaults()
    pb_core_clock(myScan.adcFrequency)

    pb_overflow(1, 0) # reset the overflow counters
    pb_scan_count(1)  # reset scan counter

    # Load the shape parameters
    make_shape_data(shape_data, num_lobes, shape_sinc)
    pb_dds_load(shape_data, DEVICE_SHAPE)
    pb_set_amp(myScan.amplitude if myScan.enable_tx else 0, 0)

    # Set acquisition parameters
    if myScan.bypass_fir:
        cmd = BYPASS_FIR

    dec_amount = pb_setup_filters(spectralWidth_MHZ, myScan.nScans, cmd)
    pb_set_num_points(myScan.nPoints)

    if dec_amount <= 0:
        if myScan.verbose:
            print("\n\nError: Invalid data returned from pb_setup_filters(). Please check your board.\n\n")
        exit(-1) # INVALID_DATA_FROM_BOARD

    actual_SW = (myScan.adcFrequency * 1e6) / float(dec_amount)
    myScan.actualSpectralWidth = actual_SW
    print("Actual Spectral Width   : %f Hz" % myScan.actualSpectralWidth)

    wait_time = 1000.0 * (float(myScan.nPoints) / actual_SW)  # time in ms
    myScan.wait_time = wait_time
    print("Acquisition Time        : %lf ms\n\n" % wait_time)

    return 0

def programBoard(myScan, cycScan):
    start = rx_start = tx_start = nLoop = 0

    pb_start_programming(FREQ_REGS)
    pb_set_freq(0)  # Program Frequency Register 0 to 0
    pb_set_freq(myScan.spectrometerFrequency * MHz)  # Register 1
    pb_set_freq(checkUndersampling(myScan, myScan.verbose))  # Register 2
    pb_stop_programming()

    # control phases for REAL channel
    pb_start_programming(COS_PHASE_REGS)
    pb_set_phase(00.0)
    pb_set_phase(90.0)
    pb_set_phase(180.0)
    pb_set_phase(270.0)
    pb_stop_programming()

    # control phases for IMAG channel
    pb_start_programming(SIN_PHASE_REGS)
    pb_set_phase(0.0)
    pb_set_phase(90.0)
    pb_set_phase(180.0)
    pb_set_phase(270.0)
    pb_stop_programming()

    # control phases for output channel
    pb_start_programming(TX_PHASE_REGS)
    pb_set_phase(myScan.tx_phase)
    pb_set_phase(myScan.tx_phase + 90.0)
    pb_set_phase(myScan.tx_phase + 180.0)
    pb_set_phase(myScan.tx_phase + 270.0)
    pb_stop_programming()
    
    #
    # Specify pulse program
    #
    
    pb_start_programming(PULSE_PROGRAM)
    nLoop = myScan.nScans // 4

    if myScan.nScans >= 4:
        # If we have the transmitter enabled, we must include the pulse program to generate the RF pulse.
        if myScan.enable_tx:
            # Reset phase initially, so that the phase of the excitation pulse will be the same for every scan.
            if pb_inst_radio_shape_cyclops(1, PHASE000, PHASE090, PHASE000, TX_DISABLE, PHASE_RESET, NO_TRIGGER, myScan.use_shape, int(myScan.amplitude), cycScan.add_sub_re_0,cycScan.add_sub_im_0, cycScan.swap_0, 0x00, CONTINUE, 0, 1.0 * us) < 0:
                print("Your board does not support CYCLOPS!\n\n")
                exit(1)

            ################## BEGIN SCAN #0 ########################
            # If blanking is enabled, we must add an additional pulse program interval to compensate for the time the power amplifier needs to "warm up" before we can generate the RF pulse.
            if myScan.blankingEnable:
                tx_start = pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_DISABLE,
                                                        NO_PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_0,
                                                        cycScan.add_sub_im_0, cycScan.swap_0, (1 << myScan.blankingBit),
                                                        LOOP, nLoop, myScan.blankingDelay * ms)
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER,
                                            myScan.use_shape, 0, cycScan.add_sub_re_0, cycScan.add_sub_im_0,
                                            cycScan.swap_0, (1 << myScan.blankingBit), CONTINUE, 0,
                                            myScan.pulseTime * us)
            else:
                tx_start = pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_ENABLE,
                                                NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0,
                                                cycScan.add_sub_re_0, cycScan.add_sub_im_0, cycScan.swap_0,
                                                0, LOOP, nLoop, myScan.pulseTime * us)
                # Output nothing for the transient time.
            pb_inst_radio_shape_cyclops (1, PHASE090, PHASE000, PHASE000, TX_DISABLE,
            			   NO_PHASE_RESET, NO_TRIGGER, 0, 0,cycScan.add_sub_re_0,cycScan.add_sub_im_0,cycScan.swap_0, 0x00, CONTINUE,
            			   0, myScan.transTime * us)
            
        # If we are enabling the receiver, we must wait for the scan to complete.
        if myScan.enable_rx:
            rx_start = pb_inst_radio_shape_cyclops (2, PHASE090, PHASE000, PHASE000, TX_DISABLE,
                                     NO_PHASE_RESET, DO_TRIGGER, 0, 0, cycScan.add_sub_re_0, cycScan.add_sub_im_0, cycScan.swap_0, 0, LONG_DELAY,
                                     8, ((myScan.wait_time)*ms/8))
        
        # If the transmitter is enabled, we start from the TX section of the pulse program.
        if myScan.enable_tx:
            start = tx_start
        elif myScan.enable_rx:
            start = rx_start
        else:
            return RX_AND_TX_DISABLED
        
        # Now wait the repetition delay, then loop back to the beginning. Also reset the phase in anticipation of the next scan.
        pb_inst_radio_shape_cyclops (1, PHASE090, PHASE000, PHASE000, TX_DISABLE, PHASE_RESET,
        		       NO_TRIGGER, 0, 0, cycScan.add_sub_re_0, cycScan.add_sub_im_0, cycScan.swap_0, 0x00, CONTINUE, 0,
         		       myScan.repetitionDelay * 1000.0 * ms)

        #################### END SCAN #0 ###########################
        
        #################### BEGIN SCAN #1 #########################
        
        if myScan.enable_tx:
            # If blanking is enabled, we must add an additional pulse program interval to compensate for the time the power amplifier needs to "warm up" before we can generate the RF pulse.
            if myScan.blankingEnable:
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE090, TX_DISABLE,
                    NO_PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_1, cycScan.add_sub_im_1, cycScan.swap_1,
                    (1 << myScan.blankingBit), CONTINUE, 0, myScan.blankingDelay * ms)
        
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE090, TX_ENABLE,
                    NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0, cycScan.add_sub_re_1, cycScan.add_sub_im_1, cycScan.swap_1,
                    (1 << myScan.blankingBit), CONTINUE, 0, myScan.pulseTime * us)
            else:
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE090, TX_ENABLE,
                    NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0, cycScan.add_sub_re_1, cycScan.add_sub_im_1, cycScan.swap_1,
                    0, CONTINUE, 0, myScan.pulseTime * us)
        
            # Output nothing for the transient time.
            pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE090, TX_DISABLE,
                NO_PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_1, cycScan.add_sub_im_1, cycScan.swap_1, 0x00, CONTINUE,
                0, myScan.transTime * us)
        
        # If we are enabling the receiver, we must wait for the scan to complete.
        if myScan.enable_rx:
            pb_inst_radio_shape_cyclops(2, PHASE090, PHASE000, PHASE090, TX_DISABLE,
                NO_PHASE_RESET, DO_TRIGGER, 0, 0, cycScan.add_sub_re_1, cycScan.add_sub_im_1, cycScan.swap_1, 0, LONG_DELAY,
                8, ((myScan.wait_time) * ms / 8))
        
        # If the transmitter is enabled, we start from the TX section of the pulse program.
        if myScan.enable_tx:
            start = tx_start
        elif myScan.enable_rx:
            start = rx_start
        else:
            return RX_AND_TX_DISABLED
        
        # Now wait the repetition delay, then loop back to the beginning. Also reset the phase in anticipation of the next scan
        pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE180, TX_DISABLE, PHASE_RESET,
            NO_TRIGGER, 0, 0, cycScan.add_sub_re_1, cycScan.add_sub_im_1, cycScan.swap_1, 0x00, CONTINUE, 0,
            myScan.repetitionDelay * 1000.0 * ms)
        
        #################### END SCAN #1 ###########################
        ################### BEGIN SCAN #2 ##########################
        if myScan.enable_tx:
            # If blanking is enabled, we must add an additional pulse program interval to compensate for the time the power amplifier needs to "warm up" before we can generate the RF pulse.
            if myScan.blankingEnable:
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE180, TX_DISABLE, NO_PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_2, cycScan.add_sub_im_2, cycScan.swap_2, (1 << myScan.blankingBit), CONTINUE, 0, myScan.blankingDelay * ms)
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE180, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0, cycScan.add_sub_re_2, cycScan.add_sub_im_2, cycScan.swap_2, (1 << myScan.blankingBit), CONTINUE, 0, myScan.pulseTime * us)
            else:
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE180, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0, cycScan.add_sub_re_2, cycScan.add_sub_im_2, cycScan.swap_2, 0, CONTINUE, 0, myScan.pulseTime * us)
        
            # Output nothing for the transient time.
            pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE180, TX_DISABLE, NO_PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_2, cycScan.add_sub_im_2, cycScan.swap_2, 0x00, CONTINUE, 0, myScan.transTime * us)
        
        # If we are enabling the receiver, we must wait for the scan to complete.
        if myScan.enable_rx:
            pb_inst_radio_shape_cyclops(2, PHASE090, PHASE000, PHASE180, TX_DISABLE, NO_PHASE_RESET, DO_TRIGGER, 0, 0, cycScan.add_sub_re_2, cycScan.add_sub_im_2, cycScan.swap_2, 0, LONG_DELAY, 8, int(myScan.wait_time * ms / 8))
        
        # Now wait the repetition delay, then loop back to the beginning. Also reset the phase in anticipation of the next scan.
        pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_DISABLE, PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_2, cycScan.add_sub_im_2, cycScan.swap_2, 0x00, CONTINUE, 0, myScan.repetitionDelay * 1000.0 * ms)
        ################# END SCAN #2 ################################

        ############### BEGIN SCAN #3 #############################
        if myScan.enable_tx:
            # If blanking is enabled, we must add an additional pulse program interval to compensate for the time the power amplifier needs to "warm up" before we can generate the RF pulse.
            if myScan.blankingEnable:
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_DISABLE,
                                            NO_PHASE_RESET, NO_TRIGGER, 0, 0,
                                            cycScan.add_sub_re_3, cycScan.add_sub_im_3, cycScan.swap_3,
                                            (1 << myScan.blankingBit), CONTINUE, 0, myScan.blankingDelay * ms)
        
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_ENABLE,
                                            NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0,
                                            cycScan.add_sub_re_3, cycScan.add_sub_im_3, cycScan.swap_3,
                                            (1 << myScan.blankingBit), CONTINUE, 0, myScan.pulseTime * us)
            else:
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_ENABLE,
                                            NO_PHASE_RESET, NO_TRIGGER, myScan.use_shape, 0,
                                            cycScan.add_sub_re_3, cycScan.add_sub_im_3, cycScan.swap_3, 0x00,
                                            CONTINUE, 0, myScan.pulseTime * us)
        
            # Output nothing for the transient time.
            pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_DISABLE,
                                        NO_PHASE_RESET, NO_TRIGGER, 0, 0,
                                        cycScan.add_sub_re_3, cycScan.add_sub_im_3, cycScan.swap_3, 0x00,
                                        CONTINUE, 0, myScan.transTime * us)
        
        # If we are enabling the receiver, we must wait for the scan to complete.
        if myScan.enable_rx:
            pb_inst_radio_shape_cyclops(2, PHASE090, PHASE000, PHASE270, TX_DISABLE,
                                        NO_PHASE_RESET, DO_TRIGGER, 0, 0,
                                        cycScan.add_sub_re_3, cycScan.add_sub_im_3, cycScan.swap_3, 0x00,
                                        LONG_DELAY, 8, ((myScan.wait_time)*ms/8))
        
        # Now wait the repetition delay, then loop back to the beginning. Also reset the phase in anticipation of the next scan.
        pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_DISABLE, PHASE_RESET,
                                    NO_TRIGGER, 0, 0,
                                    cycScan.add_sub_re_3, cycScan.add_sub_im_3, cycScan.swap_3, 0x00,
                                    END_LOOP, start, myScan.repetitionDelay * 1000.0 * ms)
        ##################### END SCAN #3 ################

    else: 
        # If we have the transmitter enabled, we must include the pulse program to generate the RF pulse.
        if myScan.enable_tx:
            # Reset phase initially, so that the phase of the excitation pulse will be the same for every scan.
            pb_inst_radio_shape_cyclops(1, PHASE000, PHASE090, PHASE000, TX_DISABLE, PHASE_RESET,
                                         NO_TRIGGER, myScan.use_shape, int(myScan.amplitude), cycScan.add_sub_re_0,
                                         cycScan.add_sub_im_0, cycScan.swap_0, 0x00, CONTINUE, 0, 1.0 * us)
        
            # If blanking is enabled, we must add an additional pulse program interval to compensate for the time the power amplifier needs to "warm up" before we can generate the RF pulse.
            if myScan.blankingEnable:
                tx_start = pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_DISABLE,
                                                        NO_PHASE_RESET, NO_TRIGGER, 0, 0, cycScan.add_sub_re_0,
                                                        cycScan.add_sub_im_0, cycScan.swap_0, (1 << myScan.blankingBit),
                                                        CONTINUE, 0, myScan.blankingDelay * ms)
        
                pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER,
                                            myScan.use_shape, 0, cycScan.add_sub_re_0, cycScan.add_sub_im_0,
                                            cycScan.swap_0, (1 << myScan.blankingBit), CONTINUE, 0, myScan.pulseTime * us)
            else:
                tx_start = pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_ENABLE, NO_PHASE_RESET,
                                                        NO_TRIGGER, myScan.use_shape, 0, cycScan.add_sub_re_0,
                                                        cycScan.add_sub_im_0, cycScan.swap_0, 0, CONTINUE, 0,
                                                        myScan.pulseTime * us)
        
            # Output nothing for the transient time.
            pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_DISABLE, NO_PHASE_RESET, NO_TRIGGER, 0, 0,
                                         cycScan.add_sub_re_0, cycScan.add_sub_im_0, cycScan.swap_0, 0x00, CONTINUE, 0,
                                         myScan.transTime * us)
        
        # If we are enabling the receiver, we must wait for the scan to complete.
        if myScan.enable_rx:
            rx_start = pb_inst_radio_shape_cyclops(2, PHASE090, PHASE000, PHASE000, TX_DISABLE, NO_PHASE_RESET, DO_TRIGGER,
                                                    0, 0, cycScan.add_sub_re_0, cycScan.add_sub_im_0, cycScan.swap_0, 0,
                                                    LONG_DELAY, 8, ((myScan.wait_time) * ms / 8))
        
        # If the transmitter is enabled, we start from the TX section of the pulse program.
        if myScan.enable_tx:
            start = tx_start
        elif myScan.enable_rx:
            start = rx_start
        else:
            exit(-1) # RX_AND_TX_DISABLED
        
        # Now wait the repetition delay, then loop back to the beginning. Also reset the phase in anticipation of the next scan.
        pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE000, TX_DISABLE, PHASE_RESET,
                                    NO_TRIGGER, 0, 0, cycScan.add_sub_re_0, cycScan.add_sub_im_0, 
                                    cycScan.swap_0, 0x00, CONTINUE, 0, myScan.repetitionDelay * 1000.0 * ms)
        
    # Stop program execution
    pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_DISABLE, NO_PHASE_RESET,
                                NO_TRIGGER, 0, 0, cycScan.add_sub_re_3, cycScan.add_sub_im_3, 
                                cycScan.swap_3, 0x00, CONTINUE, 0, 1.0 * us)
    pb_inst_radio_shape_cyclops(1, PHASE090, PHASE000, PHASE270, TX_DISABLE, NO_PHASE_RESET,
                                NO_TRIGGER, 0, 0, cycScan.add_sub_re_3, cycScan.add_sub_im_3, 
                                cycScan.swap_3, 0x00, STOP, 0, 1.0 * us)

    pb_stop_programming()
    return 0
    
def checkUndersampling(myScan, verbose):
    folding_constant = 0  
    folded_frequency = 0.0 
    adc_frequency = myScan.adcFrequency
    spectrometer_frequency = myScan.spectrometerFrequency
    nyquist_frequency = adc_frequency / 2.0

    if verbose:
        print("Specified Spectrometer Frequency: %.6f MHz" % spectrometer_frequency)
    
    if spectrometer_frequency > nyquist_frequency:
        if ((spectrometer_frequency / adc_frequency) - math.floor(spectrometer_frequency / adc_frequency)) >= 0.5:
            folding_constant = math.ceil(spectrometer_frequency / adc_frequency)
        else:
            folding_constant = math.floor(spectrometer_frequency / adc_frequency)
    
        folded_frequency = abs(spectrometer_frequency - float(folding_constant) * adc_frequency)
    
        if verbose:
            print("Undersampling Detected: Spectrometer Frequency (%.4lf MHz) is greater than Nyquist (%.4lf MHz)." % (spectrometer_frequency, nyquist_frequency))
    
        spectrometer_frequency = folded_frequency
    
    if verbose:
        print("Using Spectrometer Frequency: %.6f MHz.\n" % spectrometer_frequency)
    
    return spectrometer_frequency

def printTitleBlock(myScan, title_string):
    # These variables are used for the Title Block in Felix
    program_type = "cyclops_nmr"
    buff_string = ""     

    # Create Title Block String
    title_string += "Program = "
    title_string += program_type
    title_string += "\r\n\r\nPulse Time = "
    buff_string = str(myScan.pulseTime)
    title_string += buff_string
    title_string += "\r\nTransient Time = "
    buff_string = str(myScan.transTime)
    title_string += buff_string
    title_string += "\r\nRepetition Delay = "
    buff_string = str(myScan.repetitionDelay)
    title_string += buff_string
    title_string += "\r\n# of Scans = "
    buff_string = str(myScan.nScans)
    title_string += buff_string
    title_string += "\r\nADC Freq = "
    buff_string = str(myScan.adcFrequency)
    title_string += buff_string
    title_string += "\r\nAmplitude = "
    buff_string = str(int(myScan.amplitude))
    title_string += buff_string
    title_string += "\r\nEnable TX = "
    buff_string = str(int(myScan.enable_tx))
    title_string += buff_string
    title_string += "\r\nEnable RX = "
    buff_string = str(int(myScan.enable_rx))
    title_string += buff_string
    title_string += "\r\nVerbose = "
    buff_string = str(int(myScan.verbose))
    title_string += buff_string
    title_string += "\r\nBlanking Enable = "
    buff_string = str(myScan.blankingEnable)
    title_string += buff_string
    title_string += "\r\nBlanking Bit = "
    buff_string = str(myScan.blankingBit)
    title_string += buff_string
    title_string += "\r\nBlanking Delay = "
    buff_string = str(myScan.blankingDelay)
    title_string += buff_string
    title_string += "\r\n# of Points = "
    buff_string = str(myScan.nPoints)
    title_string += buff_string
    title_string += "\r\nSpectral Width = "
    buff_string = str(myScan.spectralWidth)
    title_string += buff_string
    title_string += "\r\nSpectrometer Freq = "
    buff_string = str(myScan.spectrometerFrequency)
    title_string += buff_string
    title_string += "\r\nBypass FIR = "
    buff_string = str(myScan.bypass_fir)
    title_string += buff_string
    title_string += "\r\nUse Shape = "
    buff_string = str(myScan.use_shape)
    title_string += buff_string


myScan = SCANPARAMS
cycScan = CYCLOPSPARAMS

#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Using SpinAPI Library version %s" % pb_get_version())
if processArguments(myScan, cycScan) == 0:
    
    # Initialize data arrays          
    real = (ctypes.c_int * myScan.nPoints)()
    imag = (ctypes.c_int * myScan.nPoints)()
    
    if myScan.verbose:
        outputScanParams(myScan)
        
    # Setup output file names
    fid_fname = myScan.outputFilename[:FNAME_SIZE]
    fid_fname = fid_fname + ".fid"[:FNAME_SIZE-len(fid_fname)]
    jcamp_fname = myScan.outputFilename[:FNAME_SIZE]
    jcamp_fname = jcamp_fname + ".jdx"[:FNAME_SIZE-len(jcamp_fname)]
    ascii_fname = myScan.outputFilename[:FNAME_SIZE]
    ascii_fname = ascii_fname + ".txt"[:FNAME_SIZE-len(ascii_fname)]
    
    if configureBoard(myScan) < 0:	# Set board defaults.
        exit(-1)
    
    if (programBoard(myScan,cycScan) != 0):	#Program the board.
        if myScan.verbose:
            print("Error: Failed to program board.\n")
        pause() 
        print('PROGRAMMING_FAILED' )
        exit(-1)
             
    pb_reset()
    pb_start()
    
    totalTime = (myScan.wait_time + (myScan.repetitionDelay * 1000)) * myScan.nScans
    
    if myScan.verbose:
        if(totalTime < 1000):
            print("Total Experiment Time   : %lf ms\n\n" % totalTime)
        elif(totalTime < 60000):
            print("Total Experiment Time   : %lf s\n\n" % (totalTime/1000))
        elif(totalTime < 3600000):
            print("Total Experiment Time   : %lf minutes\n\n" % (totalTime/60000))
        else:
            print("Total Experiment Time   : %lf hours\n\n" % (totalTime/3600000))
        
        print("Waiting for the data acquisition to complete...\n")
    
    while pb_read_status() != BOARD_STATUS_IDLE: # Wait for the board to complete execution.
        if totalTime/myScan.nScans < 600:
            pb_sleep_ms(1000)
        else:
            pb_sleep_ms(int((totalTime)/(myScan.nScans)))
        print("Current Scan: %d" % pb_scan_count(0))
    

    if myScan.enable_rx:
        
        pb_get_data(int(myScan.nPoints), real, imag)
       
        if myScan.nPoints > MAX_FFT:
            t_real[MAX_FFT]
            t_imag[MAX_FFT]
            
            for i in range(MAX_FFT):
                t_real[i] = real[i]
                t_imag[i] = imag[i]
            
            resFreq = pb_fft_find_resonance(MAX_FFT,((myScan.spectrometerFrequency)*1e6), 
                       myScan.actualSpectralWidth, t_real, t_imag)
        else:

            resFreq = pb_fft_find_resonance(myScan.nPoints, myScan.spectrometerFrequency * 1e6,
                                myScan.actualSpectralWidth, real, imag)        
               
        print("Resonance Frequency: %lf MHz\n\n" % (resFreq/1e6))
      
        printTitleBlock(myScan, title_string)
      
        pb_write_felix(fid_fname, title_string, myScan.nPoints, myScan.actualSpectralWidth, 
                      myScan.spectrometerFrequency, real, imag)
        pb_write_ascii_verbose(ascii_fname, myScan.nPoints,
    				  myScan.actualSpectralWidth,
    				  myScan.spectrometerFrequency, real, imag)
        pb_write_jcamp(jcamp_fname, myScan.nPoints,
    			  myScan.actualSpectralWidth,
    			  myScan.spectrometerFrequency, real, imag)
       # End if(enable_rx)
    pb_close()

# End if(processArguements(...)
# End main()
pause()
