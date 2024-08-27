from enum import Enum 
from typing import Type 

class PacketKeys(Enum):
    SMSG = 0            # system message 
    LFWD = 1            # forward msg along a link 
    BFWD = 2            # forward along a bus 
    DGRM = 3            # port datagram 

class NetRunnerKeys(Enum):
    RTINFO_REQ = 0      # get / recv baseline info (counts, version)
    RTINFO_RES = 1
    MTYPEGET_REQ = 2    # get a module's typename 
    MTYPEGET_RES = 3
    MNAMEGET_REQ = 4    # get a module's name 
    MNAMEGET_RES = 5
    MNAMESET_REQ = 6    # set a module's name 
    MNAMESET_RES = 7
    LINKINFO_REQ = 8    # get typeName, name and state of a link 
    LINKINFO_RES = 9
    BUSINFO_REQ = 10    # similar, for busses 
    BUSINFO_RES = 11
    PORTINFO_REQ = 12   # get a software ports' typeName and name 
    PORTINFO_RES = 13
    TIME_CONFIG_GET_REQ = 18 # get time settings 
    TIME_CONFIG_GET_RES = 19 
    TIME_CONFIG_SET_REQ = 20 # set time settings 
    TIME_CONFIG_SET_RES = 21 

class SysMsgKeys(Enum):
    TIME_STAMP_REQ = 16 # get a time stamp 
    TIME_STAMP_RES = 17 

class TransportTypeKeys(Enum):
    SEQUENTIAL_TX = 31 
    SEQUENTIAL_RX = 32 

class BuildTypeKeys(Enum):
    Embedded_CPP = 50 
    JavaScript = 51 
    Python = 52 

class OSAPValues:
    TypeNamesMaxChar = 32 
    ProperNamesMaxChar = 64 
    MaxLinkCount = 32 
    MaxPortCount = 1024 

def key_to_string(k: int, basis: Type[Enum]) -> str:
    for item in basis:
        if item.value == k:
            return item.name
    return 'unknown'