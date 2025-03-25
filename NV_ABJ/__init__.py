###################################################################################################################
# Abstract Class Types
###################################################################################################################
from NV_ABJ.abstract_device_interfaces.connected_device import ConnectedDevice
from NV_ABJ.abstract_device_interfaces.signal_generator import SignalGenerator
from NV_ABJ.abstract_device_interfaces.photon_counter import PhotonCounter
from NV_ABJ.abstract_device_interfaces.positioner import PositionerSingleAxis
from NV_ABJ.abstract_device_interfaces.scanner import ScannerSingleAxis

###################################################################################################################
# User interfaces
###################################################################################################################
from NV_ABJ.user_interfaces.hardware_user_interfaces.signal_generator_gui.signal_generator_gui import SignalGeneratorGui
from NV_ABJ.user_interfaces.hardware_user_interfaces.photon_counter_gui.photon_counter_gui import PhotonCounterGui


###################################################################################################################
# Hardware interfaces
###################################################################################################################

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Signal Generator
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from NV_ABJ.hardware_interfaces.signal_generator.sg380.sg380 import SG380, ConfigurationSG380, ChannelsSG380

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Photon Counter
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from NV_ABJ.hardware_interfaces.photon_counter.national_instruments_daq_counters.national_instruments_photon_counter_daq_controlled import NationalInstrumentsPhotonCounterDaqControlled

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Positioners
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from NV_ABJ.hardware_interfaces.positioners.cacli_jpe.cacli_jpe import CacliJpe, ConfigurationCacliJpe

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Scanner
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from NV_ABJ.hardware_interfaces.scanner.national_instruments_daq_scanner.national_instruments_daq_scanner import NationalInstrumentsDaqSingleAxisScanner, NationalInstrumentsDaqSingleAxisScannerConfiguration

###################################################################################################################
# Analyses 
###################################################################################################################

###################################################################################################################
# Experimental Logic
###################################################################################################################
from NV_ABJ.experimental_logic.confocal_scanning import ConfocalScanningControls,ConfocalScanningDisplay

###################################################################################################################
# Standard Unit Definitions  
###################################################################################################################
from enum import Enum
class SiLength(Enum):
    Tm:float = 1e12
    Gm:float  = 1e9
    Mm:float = 1e6
    km:float = 1e3
    hm:float = 1e2
    dam:float = 1e1
    m:float = 1
    dm:float = 1e-1
    cm:float = 1e-2
    mm:float = 1e-3
    um:float = 1e-6
    nm:float = 1e-9
    pm:float = 1e-12

class SiTime(Enum):
    Ts:float = 1e12
    Gs:float  = 1e9
    Ms:float = 1e6
    ks:float = 1e3
    hs:float = 1e2
    das:float = 1e1
    s:float = 1
    ds:float = 1e-1
    cs:float = 1e-2
    ms:float = 1e-3
    us:float = 1e-6
    ns:float = 1e-9
    ps:float = 1e-12

class SiMass(Enum):
    Tg:float = 1e12
    Gg:float  = 1e9
    Mg:float = 1e6
    kg:float = 1e3
    hg:float = 1e2
    dag:float = 1e1
    g:float = 1
    dg:float = 1e-1
    cg:float = 1e-2
    mg:float = 1e-3
    ug:float = 1e-6
    ng:float = 1e-9
    pg:float = 1e-12










































# # # #                         .       .
# # # #                        / `.   .' \
# # # #                .---.  <    > <    >  .---.
# # # #                |    \  \ - ~ ~ - /  /    |
# # # #                 ~-..-~             ~-..-~
# # # #             \~~~\.'                    `./~~~/
# # # #              \__/                        \__/
# # # #               /                  .-    .  \
# # # #        _._ _.-    .-~ ~-.       /       }   \/~~~/
# # # #    _.-'q  }~     /       }     {        ;    \__/
# # # #   {'__,  /      (       /      {       /      `. ,~~|   .     .
# # # #    `''''='~~-.__(      /_      |      /- _      `..-'   \\   //
# # # #                / \   =/  ~~--~~{    ./|    ~-.     `-..__\\_//_.-'
# # # #               {   \  +\         \  =\ (        ~ - . _ _ _..---~
# # # #               |  | {   }         \   \_\
# # # #              '---.o___,'       .o___,'     "by--Maxim--max107"
# # # # 