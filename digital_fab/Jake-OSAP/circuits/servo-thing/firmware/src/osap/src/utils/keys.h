// keys 

#ifndef KEYS_H_
#define KEYS_H_

#include <Arduino.h>


// are [0:1] in a byte 

// system message 
#define PKEY_SMSG 0  
// point forwards: send the packt along a point-to-point link 
#define PKEY_LFWD 1
// bus forwards: send the packet on a bus 
#define PKEY_BFWD 2  
// port datagram: the packet is a datagram for a port in this module 
#define PKEY_DGRM 3  


// bits [3:7] (0-31) in a SMSG 

// get runtime info
#define SKEY_RTINFO_REQ 0
#define SKEY_RTINFO_RES 1
// get module type
#define SKEY_MTYPEGET_REQ 2
#define SKEY_MTYPEGET_RES 3
// get module name
#define SKEY_MNAMEGET_REQ 4
#define SKEY_MNAMEGET_RES 5
// set module name
#define SKEY_MNAMESET_REQ 6
#define SKEY_MNAMESET_RES 7
// get point-link info
#define SKEY_LINKINFO_REQ 8
#define SKEY_LINKINFO_RES 9
// get bus-link info
#define SKEY_BUSINFO_REQ 10
#define SKEY_BUSINFO_RES 11
// get port info
#define SKEY_PORTINFO_REQ 12
#define SKEY_PORTINFO_RES 13

// get time settings 
#define SKEY_TIME_CONFIG_GET_REQ 18 
#define SKEY_TIME_CONFIG_GET_RES 19 

// set time settings 
#define SKEY_TIME_CONFIG_SET_REQ 20 
#define SKEY_TIME_CONFIG_SET_RES 21 

// get a time stamp 
#define SKEY_TIME_STAMP_REQ 16 
#define SKEY_TIME_STAMP_RES 17 


// transport protocol keys 
#define TKEY_SEQUENTIAL_TX 31 
#define TKEY_SEQUENTIAL_RX 32

// basically enums 

// keys for build types 
#define BUILDTYPEKEY_EMBEDDED_CPP 50
#define BUILDTYPEKEY_JAVASCRIPT 51
#define BUILDTYPEKEY_PYTHON 52


#endif 