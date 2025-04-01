__all__ = ["meters","seconds","grams","hertz","volts","amps","kelvin","candela","watts","joules","mols","liters"]
"""This is a standard units file to enforce the use of valid units and to set an expected base unit for classes while not limiting the user
"""
from enum import Enum
class meters(Enum):
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

class seconds(Enum):
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

class grams(Enum):
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

class hertz(Enum):
    THz:float = 1e12
    GHz:float  = 1e9
    MHz:float = 1e6
    kHz:float = 1e3
    hHz:float = 1e2
    daHz:float = 1e1
    Hz:float = 1
    dHz:float = 1e-1
    cHz:float = 1e-2
    mHz:float = 1e-3
    uHz:float = 1e-6
    nHz:float = 1e-9
    pHz:float = 1e-12

class volts(Enum):
    TV:float = 1e12
    GV:float  = 1e9
    MV:float = 1e6
    kV:float = 1e3
    hV:float = 1e2
    daV:float = 1e1
    V:float = 1
    dV:float = 1e-1
    cV:float = 1e-2
    mV:float = 1e-3
    uV:float = 1e-6
    nV:float = 1e-9
    pV:float = 1e-12

class amps(Enum):
    TA:float = 1e12
    GA:float  = 1e9
    MA:float = 1e6
    kA:float = 1e3
    hA:float = 1e2
    daA:float = 1e1
    A:float = 1
    dA:float = 1e-1
    cA:float = 1e-2
    mA:float = 1e-3
    uA:float = 1e-6
    nA:float = 1e-9
    pA:float = 1e-12

class kelvin(Enum):
    TK:float = 1e12
    GK:float  = 1e9
    MK:float = 1e6
    kK:float = 1e3
    hK:float = 1e2
    daK:float = 1e1
    K:float = 1
    dK:float = 1e-1
    cK:float = 1e-2
    mK:float = 1e-3
    uK:float = 1e-6
    nK:float = 1e-9
    pK:float = 1e-12

class candela(Enum):
    Tcd:float = 1e12
    Gcd:float  = 1e9
    Mcd:float = 1e6
    kcd:float = 1e3
    hcd:float = 1e2
    dacd:float = 1e1
    cd:float = 1
    dcd:float = 1e-1
    ccd:float = 1e-2
    mcd:float = 1e-3
    ucd:float = 1e-6
    ncd:float = 1e-9
    pcd:float = 1e-12

class watts(Enum):
    TW:float = 1e12
    GW:float  = 1e9
    MW:float = 1e6
    kW:float = 1e3
    hW:float = 1e2
    daW:float = 1e1
    W:float = 1
    dW:float = 1e-1
    cW:float = 1e-2
    mW:float = 1e-3
    uW:float = 1e-6
    nW:float = 1e-9
    pW:float = 1e-12

class joules(Enum):
    TJ:float = 1e12
    GJ:float  = 1e9
    MJ:float = 1e6
    kJ:float = 1e3
    hJ:float = 1e2
    daJ:float = 1e1
    J:float = 1
    dJ:float = 1e-1
    cJ:float = 1e-2
    mJ:float = 1e-3
    uJ:float = 1e-6
    nJ:float = 1e-9
    pJ:float = 1e-12

class mols(Enum):
    Tmol:float = 1e12
    Gmol:float  = 1e9
    Mmol:float = 1e6
    kmol:float = 1e3
    hmol:float = 1e2
    damol:float = 1e1
    mol:float = 1
    dmol:float = 1e-1
    cmol:float = 1e-2
    mmol:float = 1e-3
    umol:float = 1e-6
    nmol:float = 1e-9
    pmol:float = 1e-12

class liters(Enum):
    Tl:float = 1e12
    Gl:float  = 1e9
    Ml:float = 1e6
    kl:float = 1e3
    hl:float = 1e2
    dal:float = 1e1
    l:float = 1
    dl:float = 1e-1
    cl:float = 1e-2
    ml:float = 1e-3
    ul:float = 1e-6
    nl:float = 1e-9
    pl:float = 1e-12
























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