// runtime !

#include "runtime.h"
#include "../packets/packets.h"
#include "../utils/serdes.h"
#include "../utils/random_sequence_gen.h"
#include "../utils/platform_flash.h"
#include "../utils/micros_64.h"
#include "../utils/debug.h"
#include "../osap_config.h"

#include "../discovery/netresponder.h"

// ---------------------------------------------- Singleton

OSAP_Runtime* OSAP_Runtime::instance = nullptr;

OSAP_Runtime* OSAP_Runtime::getInstance(void){
  return instance;
}

// and a coupl'a static-stashes 

void (*OSAP_Runtime::printFuncPtr)(String) = nullptr;

Route OSAP_Runtime::_route;

uint8_t OSAP_Runtime::_payload[OSAP_CONFIG_PACKET_MAX_SIZE];

// ---------------------------------------------- Message Stack and Constructor

// stack size modifies how much memory the device sucks, 
// it should be configured per-micro-platform (?) or sth, 
// we need some arduino help... other options are to expose 
// memory allocation to the user, but it's a little awkward 

VPacket _stack[OSAP_CONFIG_STACK_SIZE];

OSAP_Runtime::OSAP_Runtime(const char* _typeName, const char* _name){
  // we're the one & only, unless we aren't, 
  if(instance != nullptr) return; 
  instance = this;
  
  // collect stack from the file scope,
  stack = _stack;
  stackSize = OSAP_CONFIG_STACK_SIZE;

  // copy and check names, 
  strncpy(typeName, _typeName, OSAP_PROPERNAMES_MAX_CHAR);
  typeName[OSAP_PROPERNAMES_MAX_CHAR - 1] = '\0';

  // startup the platform flash (req'd for next steps) 
  flashBegin();

  // now we have a few cases for the module's name:
  if(strcmp(_name, "anon") == 0){
    if(flashNameStorageCheck()){
      // pull from flash to name, 
      flashCopySavedNameInto(moduleName);
    } else {
      // generate a randy five-chars after the given typeName_ 
      strncpy(moduleName, typeName, OSAP_PROPERNAMES_MAX_CHAR);
      randomGenAddChars(moduleName, OSAP_PROPERNAMES_MAX_CHAR);
    }
  } else {
    // when osap(typeName, properName) is used, always start-up with 
    // the given proper name: these are manually-configured systems 
    strncpy(moduleName, _name, OSAP_PROPERNAMES_MAX_CHAR);
    moduleName[OSAP_PROPERNAMES_MAX_CHAR - 1] = '\0';    
  }

  // and we build our responder on port-zero by default, 
  responder = new NetResponder();

} // end cnstructor 

OSAP_Runtime::OSAP_Runtime(const char* _typeName):OSAP_Runtime(_typeName, "anon"){};

void OSAP_Runtime::begin(void){
  // startup linked-list, 
  stackReset(stack, stackSize);
  // for each link in list, do link->begin();
  for(uint16_t l = 0; l < linkCount; l ++){
    links[l]->begin();
  }
  // for each port, do port->begin();
  for(uint16_t p = 0; p < portCount; p ++){
    ports[p]->begin();
  }
}

// ---------------------------------------------- Time Service

uint64_t OSAP_Runtime::calculateSystemMicroseconds(bool interval = false){
  // get current stamp w/ underlying clock and stash that pt for long integral 
  uint64_t underlyingStamp = micros64();
  uint64_t underlyingInterval = underlyingStamp - underlyingStampPrevious;
  // TODO: can we avoid having 'underlyingStampPrevious' ? 
  if(interval) underlyingStampPrevious = underlyingStamp;
  // return timeBaseAtLastCalculation + underlyingInterval; 
  // we can shim that interval... 
  fpint64_t shimmedInterval = fp_mult64x64_bigLittle(fp_int64ToFixed64(underlyingInterval), clockSkew);
  return timeBaseAtLastCalculation + fp_fixed64ToInt64(shimmedInterval);
  // return fp_fixed64ToInt64(shimmedInterval);
}

uint64_t OSAP_Runtime::getSystemMicroseconds(void){
  return calculateSystemMicroseconds(false);
}

void OSAP_Runtime::setSystemMicroseconds(uint64_t _us){
  timeBaseAtLastCalculation = _us; 
  underlyingStampPrevious = micros64();
}

float OSAP_Runtime::getClockSkewAsFloat(void){
  return fp_fixed64ToFloat32(clockSkew);
}

void OSAP_Runtime::timeLoop(void){
  // occasionally accumulate the interval 
  if(underlyingStampPrevious + timeCalcInterval < micros64()){
    timeBaseAtLastCalculation = calculateSystemMicroseconds(true);
  }
  // occasionally ping others for time measurements 
  if(timeQueryLastTime + timeQueryInterval < micros64()){
    if(!claimPacketCheck(this)) return;
    timeQueryLastTime = micros64();
    // rollover whomst we will poll, 
    timeQueryRecipient ++;
    if(timeQueryRecipient >= linkCount) timeQueryRecipient = 0;
    // author a new outgoing packet (will need to modify this for us...)
    VPacket* pck = claimPacketFromStack(this);
    // it'll go along such-and-such a route: 
    _route.reset();
    _route.addLink(timeQueryRecipient);
    _route.setTimeToLive(32000);
    _route.setMaxSegmentSize(64);
    // assemble a datagram, 
    size_t wptr = 0;
    _payload[wptr ++] = 0 | PKEY_SMSG << 6 | SKEY_TIME_STAMP_REQ;
    // we use this time *just* to calculate an RTT, so we can use the underlying, 
    // although in high-skew scenarios this may be non optimal (?) the noise floor is 
    // much higher than clock shim digits 
    serializeTight<uint64_t>(micros64(), _payload, &wptr);
    // ship-it 
    stuffPacketRaw(pck, &_route, _payload, wptr);
  }
}

void OSAP_Runtime::timeOnStampReturn(uint8_t link, uint8_t tier, uint64_t txTime, uint64_t stamp){
  // now we can do rtt, which is based on our underlying clock 
  // and use that to estimate their current time 
  uint32_t rtt = micros64() - txTime; 
  uint64_t senderTime = stamp + rtt / 2;
  int64_t offset = senderTime - getSystemMicroseconds();

  // we'll store each link's measured offset and reported tier 
  perLinkTimeStats[link].offset = offset; 
  perLinkTimeStats[link].tier = tier;

  // then we should recalculate: using our first reference to the highest tier
  uint8_t maxTier = 255;
  uint8_t tierCount = 0; 
  for(uint8_t l = 0; l < linkCount; l ++){
    if(perLinkTimeStats[l].tier < maxTier) {
      maxTier = perLinkTimeStats[l].tier;
      if(maxTier != 255) ourTimeTier = maxTier + 1;
    }
  }
  for(uint8_t l = 0; l < linkCount; l ++){
    if(perLinkTimeStats[l].tier == maxTier) tierCount ++;
  }

  // we should only bother updating our own parameters if we have just rx'd new info 
  // from the max tier:
  if(maxTier != tier) return;

  // TODO would be to add an average when we have multiple counts at the max tier... 
  // as would probably be the case in big autonomous meshes, for now we just take the first: 
  if(!tierCount) return; 
  int64_t targetOffset = 0;
  for(uint8_t l = 0; l < linkCount; l ++){
    if(perLinkTimeStats[l].tier == maxTier){
      targetOffset = perLinkTimeStats[l].offset;
      break; 
    }
  }

  // then we run our olden algo:   
  // if their clock is ahead by more than 100ms, we should use it as a baseline:
  // but only if their tier out-strips ours 
  if((useHardOffsetJumps && targetOffset > clockOffsetHardTrigger) || (targetOffset < -clockOffsetHardTrigger && maxTier < ourTimeTier)){
    setSystemMicroseconds(timeBaseAtLastCalculation + targetOffset);
    clockSkew = fp_int64ToFixed64(1);
    lastHardReset = micros64();
  } else if(useHardOffsetJumps && targetOffset > clockOffsetHardTrigger){
    setSystemMicroseconds(timeBaseAtLastCalculation + targetOffset);
    clockSkew = fp_int64ToFixed64(1);
    lastHardReset = micros64();
  } else if (targetOffset < - clockOffsetHardTrigger){
    // an important do-nothing step, lest we chase tails 
  } else {
    // before we update the skew, we need to accumulate using the most recent skew, 
    // otherwise we risk shifting the current time into the past, or jumping to the future, etc 
    timeBaseAtLastCalculation = calculateSystemMicroseconds(true);
    // now we can set, basically 1.0 +/- some tiny skew, 
    // which is just proportional to the offset 
    uint64_t propNow = fp_mult64x64_bigLittle(fp_int64ToFixed64(targetOffset), clockSkewProportionalTerm);
    // and which is filtered, 
    propTerm = 
      fp_mult64x64_bigLittle(propTerm, propFilterAlpha) + 
      fp_mult64x64_bigLittle(propNow, propFilterOneMinusAlpha);
    // let's clamp it, 
    if(propTerm > fp_float32ToFixed64(0.00015F)) propTerm = fp_float32ToFixed64(0.00015F);
    if(propTerm < fp_float32ToFixed64(-0.00015F)) propTerm = fp_float32ToFixed64(-0.00015F);
    // then term +/- 1 is the skew... 
    clockSkew = fp_int64ToFixed64(1) + propTerm;
  }
}


// ---------------------------------------------- Core Runtime Loop 

// at most we can handle every single packet in 
// the system during one loop, so here's the ordered list of 'em
VPacket* packets[OSAP_CONFIG_STACK_SIZE];

void OSAP_Runtime::loop(void){
  // (00) run time service 
  timeLoop();

  // (0) check the time... this should use system time eventually
  uint32_t now = micros();

  // (1) run each links' loop code:
  for(uint16_t l = 0; l < linkCount; l ++){
    if(links[l] != nullptr) links[l]->loop();
  }

  // (2) collect paquiats from the staquiat,
  size_t count = stackGetPacketsToService(packets, OSAP_CONFIG_STACK_SIZE);
  if(count > debug_stackServiceHighWaterMark) debug_stackServiceHighWaterMark = count;

  // (2.5 TODO) packets are sorted insertion-order already, in the future we can 
  // re-sort by timeToLive, 

  // (3) operate per-packet, 
  for(uint8_t p = 0; p < count; p ++){

    // (3:1) time out deadies, 
    #warning TODO: TIME TO LIVE
    if(packets[p]->serviceDeadline < now){
      OSAP_DEBUG("packet t/o: " + String(packets[p]->data[packets[p]->data[0]]));
      debug_totalPacketsTimedOut ++;
      relinquishPacketToStack(packets[p]);
      continue;
    }

    // (3:2) service the packet's instruction, 
    // ... pck[0] is a pointer to the active instruction, 
    // so pck[pck[0]] == OPCODE, basically 
    VPacket* pck = packets[p];
    uint8_t ptr = pck->data[0];
    switch(pck->data[ptr] >> 6){
      // -------------------- Packets destined for a port in this runtime:
      case PKEY_DGRM:
        {
          // ... haven't tested this bitwise logic yet !
          uint16_t sourceIndex = (uint16_t)(pck->data[ptr] & 0b00001111) << 6 | (pck->data[ptr + 1] & 0b11111100) >> 2;
          uint16_t destinationIndex = (uint16_t)(pck->data[ptr + 1] & 0b00000011) << 2 | pck->data[ptr + 2];
          if(destinationIndex < portCount && ports[destinationIndex] != nullptr){
            // we want to hand the recipient the route *back to* the sender, 
            getRouteFromPacket(pck, &_route);
            _route.reverse();
            // copying the data out, since pck is potentially re-allocated during next steps 
            size_t payloadLen = pck->len - (ptr + 3);
            memcpy(_payload, &(pck->data[ptr + 3]), payloadLen);
            // now we can de-allocate this pck and hand the datagram off, 
            relinquishPacketToStack(pck);
            ports[destinationIndex]->onPacket(_payload, payloadLen, &_route, sourceIndex);
          } else {
            OSAP_ERROR("dgrm for non-existent port: " + String(destinationIndex));
            relinquishPacketToStack(pck);
          }
        }
        break;
      // -------------------- Packet to forwards along a point link 
      case PKEY_LFWD:
        {
          uint8_t index = pck->data[ptr] & 0b00011111;
          if(index < linkCount && links[index] != nullptr){
            if(links[index]->clearToSend()){
              // TODO: need to decriment the packet's time-to-live (!) 
              links[index]->send(pck->data, pck->len);
              relinquishPacketToStack(pck);
            }
          } else {
            OSAP_ERROR("pfwd for non-existent link: " + String(index));
            relinquishPacketToStack(pck);
          }
        }
        break;
      // -------------------- Packet to forwards along a bus link
      case PKEY_BFWD:
        // TODO: busses, lol 
        OSAP_DEBUG("bus-fwds key in the runtime...");
        relinquishPacketToStack(pck);
        break;
      // -------------------- System Messages (mostly for discovery)
      case PKEY_SMSG:
        handleSystemMessage(pck);
        break;
    } // end switch 
  } // end for-p-in-packets 
} // end loop 

void OSAP_Runtime::handleSystemMessage(VPacket* pck){
  uint8_t ptr = pck->data[0];
  switch(pck->data[ptr] & 0b00011111){
      // -------------------- Time Service  
    case SKEY_TIME_STAMP_REQ:
      {
        // stuff a stamp *trailing* the sender's own, which is at [1] (8 byte)
        _payload[0] = 0 | PKEY_SMSG << 6 | SKEY_TIME_STAMP_RES;
        // sender's tx time is in there, copy it over:
        memcpy(_payload + 1, pck->data + ptr + 1, 8);
        // and stuff ours in the trunk; 
        size_t wptr = 9;
        serializeTight<uint64_t>(getSystemMicroseconds(), _payload, &wptr);
        serializeTight<uint8_t>(ourTimeTier, _payload, &wptr);
        // sendy 
        reply(pck, _payload, 18);
      }
      break;
    case SKEY_TIME_STAMP_RES:
      {
        size_t rptr = ptr + 1;
        // our tx time was a stamp from our *underlying* clock 
        uint64_t txTime = deserializeTight<uint64_t>(pck->data, &rptr);
        // if this was tx'd prior to a hard reset to our own clock, we should ignore the stamp, 
        if(lastHardReset < txTime){
          // their stamp is based on their *system* clock (our target) 
          uint64_t stamp = deserializeTight<uint64_t>(pck->data, &rptr);
          // and their tier:
          uint8_t tier = deserializeTight<uint8_t>(pck->data, &rptr);
          // these only ever hop once, so incoming port is in a fixed location:
          uint8_t link = pck->data[5] & 0b00111111;
          // now we can do the action 
          timeOnStampReturn(link, tier, txTime, stamp);
        }
        // exit and give up the packet 
        relinquishPacketToStack(pck);
      }
      break;
    // inspect and mux with 
  }

}

void OSAP_Runtime::reply(VPacket* pck, uint8_t* data, size_t len){
  // extract the route & reverse it, 
  getRouteFromPacket(pck, &_route);
  // OSAP_DEBUG(OSAP_DEBUG_PRINT_ROUTE(&_route));
  _route.reverse();
  // OSAP_DEBUG(OSAP_DEBUG_PRINT_ROUTE(&_route));
  // since the packet is already allocated (wherever the msg was sourced)
  // we can just bonk it back in, i.e. re-write to the same data location:
  stuffPacketRaw(pck, &_route, data, len);
  // that's actually all there is to it (!) the reply is now loaded in, runtime collects & manages 
}

// ---------------------------------------------- Debug Funcs and Attach-er

void OSAP_Runtime::attachDebugFunction(void (*_printFuncPtr)(String)){
  OSAP_Runtime::printFuncPtr = _printFuncPtr;
}

void OSAP_Runtime::error(String msg){
  if(printFuncPtr == nullptr) return;
  OSAP_Runtime::printFuncPtr(msg);
}

void OSAP_Runtime::debug(String msg){
  if(printFuncPtr == nullptr) return;
  OSAP_Runtime::printFuncPtr(msg);
}

#ifdef OSAP_CONFIG_INCLUDE_DEBUG_MSGS

String OSAP_Runtime::printRoute(Route* route){
  String msg;
  // this could be ~ fancier, i.e. decoding as well... 
  // see routes.ts::print for an example
  for(uint8_t p = 0; p < route->encodedPathLen; p ++){
    msg += String(route->encodedPath[p]) + ", ";
  }
  return msg;
}

String OSAP_Runtime::printPacket(VPacket* pck){
  String msg;
  for(uint8_t b = 0; b < pck->len; b ++){
    msg += String(pck->data[b]) + ",";
  }
  return msg;
}

#endif 