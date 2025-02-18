/*
osap_config.h

config options for an osap-embedded build

Jake Read at the Center for Bits and Atoms
(c) Massachusetts Institute of Technology 2022

This work may be reproduced, modified, distributed, performed, and
displayed for any purpose, but must acknowledge the osap project.
Copyright is retained and must be preserved. The work is provided as is;
no warranty is provided, and users accept all liability.
*/

#ifndef OSAP_CONFIG_H_
#define OSAP_CONFIG_H_

// -------------------------------- Track Version - Num 

// i.e. 0.1.2 
// MAJOR: 0, 
// MID: 1,
// MINOR: 2

#define OSAP_VERSION_MAJOR 0 
#define OSAP_VERSION_MID 7
#define OSAP_VERSION_MINOR 1

// -------------------------------- Stack / Build Sizes

// TODO: we have from i.e. COBSUSBSerial.cpp examples of `if defined(ARDUINO_ARCH...)
// - we should use those to set relative stack sizes for typical RAM avail
// and should also watch out to perhaps set compiler flags for RP2040 to allocate 
// these buffers in RAM rather than slow-af SRAM  

#define OSAP_CONFIG_STACK_SIZE 6
#define OSAP_CONFIG_PACKET_MAX_SIZE 256

#define OSAP_CONFIG_MAX_PORTS 32
#define OSAP_CONFIG_MAX_LGATEWAYS 16
#define OSAP_CONFIG_MAX_BGATEWAYS 8

#define OSAP_CONFIG_ROUTE_MAX_LENGTH 64 

#define OSAP_CONFIG_DEFAULT_SERVICE_DEADLINE 20000

// -------------------------------- Name Lengths

// more of a protocol feature: typenames need to be < 32 char, names < 64 ! 

#define OSAP_TYPENAMES_MAX_CHAR 32 
#define OSAP_PROPERNAMES_MAX_CHAR 64 

// -------------------------------- Error / Debug Build Options 

#define OSAP_CONFIG_INCLUDE_DEBUG_MSGS
#define OSAP_CONFIG_INCLUDE_ERROR_MSGS

#endif
