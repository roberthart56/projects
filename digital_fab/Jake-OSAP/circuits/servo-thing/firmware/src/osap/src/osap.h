/*
osap/osap.h

osap root / vport factory

Jake Read at the Center for Bits and Atoms
(c) Massachusetts Institute of Technology 2021

This work may be reproduced, modified, distributed, performed, and
displayed for any purpose, but must acknowledge the squidworks and ponyo
projects. Copyright is retained and must be preserved. The work is provided as
is; no warranty is provided, and users accept all liability.
*/

#ifndef OSAP_H_
#define OSAP_H_

// our osap.h include is ~ just a pointer to whatever 
// components we are going to present at a "high level" 

#include "runtime/runtime.h"
#include "utils/debug.h"

// we could also do config-dependent include of various links...
#include "gateway_integrations/link_usb_cdc_cobs.h"
#include "gateway_integrations/link_uart_cobs_crc16.h"

// and of port types...
#include "presentation/port_rpc.h"

#define BUILD_RPC(func, args, returns)\
    OSAP_Port_RPC<decltype(&func)> func##_rpc(&func, #func, args, returns)

// to use auto-dispatched macro: 

/*
#define BUILD_RPC_3(func, args, returns)\
    OSAP_Port_RPC<decltype(&func)> func##_rpc(&func, #func, args, returns)

#define BUILD_RPC_2(func, args)\
    OSAP_Port_RPC<decltype(&func)> func##_rpc(&func, #func, args, "")

#define BUILD_RPC_1(func)\
    OSAP_Port_RPC<decltype(&func)> func##_rpc(&func, #func, "", "")

// dispatcher macros 
#define GET_MACRO(_1,_2,_3,NAME,...) NAME

// ARGS: function, "argument_names", "return_names"
#define BUILD_RPC(...)\
    GET_MACRO(__VA_ARGS__, BUILD_RPC_3, BUILD_RPC_2, BUILD_RPC_1)(__VA_ARGS__)
*/

// #include "presentation/port_bare.h"
// #include "presentation/port_pipe.h"

// #include "presentation/port_deviceNames.h"
// #include "presentation/port_messageEscape.h"


#endif
