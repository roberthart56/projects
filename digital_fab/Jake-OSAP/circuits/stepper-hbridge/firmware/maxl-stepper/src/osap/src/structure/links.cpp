// links ! 

#include "links.h"
#include "../packets/packets.h"
#include "../utils/serdes.h"
#include "../utils/random_sequence_gen.h"

#include "../utils/debug.h"

LinkGateway::LinkGateway(OSAP_Runtime* _runtime, const char* _typeName, const char* _name){
  // track our runtime, 
  runtime = _runtime;

  // don't over-insert: 
  if(runtime->linkCount >= OSAP_CONFIG_MAX_LGATEWAYS){
    OSAP_ERROR("too many links instantiated...");
    return;
  }
  
  // collect our index and stash ourselves in the runtime, 
  index = runtime->linkCount;
  runtime->links[runtime->linkCount ++] = this;

  // copy-in names, respecting limits 
  strncpy(typeName, _typeName, OSAP_TYPENAMES_MAX_CHAR);
  strncpy(name, _name, OSAP_PROPERNAMES_MAX_CHAR);
  // strncpy does not pad with spare '\0' in the case that charlimit exceeded 
  typeName[OSAP_TYPENAMES_MAX_CHAR - 1] = '\0';
  name[OSAP_PROPERNAMES_MAX_CHAR - 1] = '\0';

  // names should be unique within a system, 
  for(uint8_t p = 0; p < runtime->linkCount; p ++){
    if(p == index) continue;
    if(strcmp(name, runtime->links[p]->name) == 0){
      randomGenAddChars(name, OSAP_PROPERNAMES_MAX_CHAR);
    }
  }
}

void LinkGateway::ingestPacket(VPacket* pck){
  // this should be the case, badness if not
  // since we should be only rx'ing from someone's prior LFWD instruction... 
  if(pck->data[pck->data[0]] >> 6 != PKEY_LFWD){
    OSAP_ERROR("bad PTR during packet ingest at link " + String(index));
    relinquishPacketToStack(pck);
    return;
  }
  // otherwise copy-in our index for rev-ersal,
  pck->data[pck->data[0]] = PKEY_LFWD << 6 | index;
  // bump the pointer up, 
  pck->data[0] += 1;
  // and calculate a service deadline, 
  size_t rptr = 1;
  uint16_t timeToLive = deserializeTight<uint16_t>(pck->data, &rptr);
  pck->serviceDeadline = micros() + timeToLive;
}