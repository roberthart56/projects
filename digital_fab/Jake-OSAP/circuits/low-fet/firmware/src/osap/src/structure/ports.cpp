// pert pert pert 

#include "ports.h"
#include "../packets/packets.h"
#include "../utils/random_sequence_gen.h"

#include "../utils/debug.h"

// default constructor 
VPort::VPort(OSAP_Runtime* _runtime, const char* _typeName, const char* _name){
  // track our runtime, 
  runtime = _runtime;

  // don't over-insert: 
  if(runtime->portCount >= OSAP_CONFIG_MAX_PORTS){
    OSAP_ERROR("too many ports instantiated...");
    return;
  } 
  
  // collect our index and stash ourselves in the runtime, 
  index = runtime->portCount;
  runtime->ports[runtime->portCount ++] = this;

  // copy-in names, respecting limits 
  strncpy(typeName, _typeName, OSAP_TYPENAMES_MAX_CHAR);
  strncpy(name, _name, OSAP_PROPERNAMES_MAX_CHAR);
  // strncpy does not pad with spare '\0' in the case that charlimit exceeded 
  typeName[OSAP_TYPENAMES_MAX_CHAR - 1] = '\0';
  name[OSAP_PROPERNAMES_MAX_CHAR - 1] = '\0';

  // if we were given "anon" we rollup a new name, 
  if(strcmp(_name, "anon") == 0){
    strncpy(name, typeName, OSAP_PROPERNAMES_MAX_CHAR);
    randomGenAddChars(name, OSAP_PROPERNAMES_MAX_CHAR);
  }

  // names should be unique within a system, 
  for(uint8_t p = 0; p < runtime->portCount; p ++){
    if(p == index) continue;
    if(strcmp(name, runtime->ports[p]->name) == 0){
      randomGenAddChars(name, OSAP_PROPERNAMES_MAX_CHAR);
    }
  }
}

uint8_t VPort::_payload[OSAP_CONFIG_PACKET_MAX_SIZE];

void VPort::begin(void){};

boolean VPort::clearToSend(void){
  return claimPacketCheck(this);
}

void VPort::send(uint8_t* data, size_t len, Route* route, uint16_t destinationPort){
  // allocate & check, 
  VPacket* pck = claimPacketFromStack(this);
  if(pck == nullptr) {
    OSAP_ERROR("bad packet allocate on vport.send() at " + String(index));
    return;
  }
  // stuff it, 
  stuffPacketPortToPort(pck, route, index, destinationPort, data, len);
  // I think that's actually it ? 
}