
#include "netresponder.h"
#include "../runtime/runtime.h"
#include "../structure/links.h"
#include "../utils/serdes.h"
#include "../utils/micros_64.h"
#include "../utils/platform_flash.h"
#include "../utils/debug.h"

NetResponder::NetResponder(void) : OSAP_Sequential_Receiver("netresponder", "netresponder"){
  rt = OSAP_Runtime::getInstance();
}

size_t NetResponder::onData(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort, uint8_t* reply){
  switch(data[0] & 0b00011111){
    // -------------------- Discovery Service 
    case SKEY_RTINFO_REQ:
      {
        // response key w/ matching message id, 
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_RTINFO_RES;
        // handoff thet traverse id, bytes 2,3,4,5
        memcpy(reply + 1, rt->previousTraverseID, 4);
        memcpy(rt->previousTraverseID, data + 1, 4);
        // report our build type and version, 
        reply[5] = BUILDTYPEKEY_EMBEDDED_CPP;
        reply[6] = OSAP_VERSION_MAJOR;
        reply[7] = OSAP_VERSION_MID;
        reply[8] = OSAP_VERSION_MINOR;
        // report the instruction of arrival, 
        memcpy(reply + 9, sourceRoute->encodedPath, 2);
        // if this was a self-scan, we will have zero route, so need to stuff
        // a meaningless 'smsg' key in here... 
        if(sourceRoute->encodedPathLen == 0){
          reply[9] = PKEY_SMSG << 6;
          reply[10] = 0;
        }
        // point link count B12[3:7], bus link count B13[0:5], and port count B13[6:7],B14[0:7]
        reply[11] = 0b00011111 & rt->linkCount;
        // ... no busses here, so just carry on  
        reply[12] = 0b00000011 & (rt->portCount >> 8);
        reply[13] = rt->portCount & 0b11111111;
        // that's all, ship it inline 
        return 14;
      }
    // -------------------- Requesting the module's type name 
    case SKEY_MTYPEGET_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_MTYPEGET_RES;
        // reporting *module's* version nums, but basically a protocol placeholder, so:
        reply[1] = 0; 
        reply[2] = 0; 
        reply[3] = 0;
        // stuff the typename 
        size_t wptr = 4;
        serializeTight<char*>(rt->typeName, reply, &wptr);
        return wptr;
      }
    // -------------------- Requesting the module's own name 
    case SKEY_MNAMEGET_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_MNAMEGET_RES;
        // stuff the module's name, 
        size_t wptr = 1;
        serializeTight<char*>(rt->moduleName, reply, &wptr);
        return wptr;
      }
    // -------------------- Requesting to change the module's own name 
    case SKEY_MNAMESET_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_MNAMESET_RES;
        // we're going to read straight from the packet into the name-field, 
        size_t rptr = 1;
        deserializeTightInto<char*>(rt->moduleName, data, &rptr, OSAP_PROPERNAMES_MAX_CHAR); 
        // and then commit that to flash (TODO)
        flashSaveName(rt->moduleName);
        // and reply w/ an OK (if we have flash capability, elsewise reply as ungovernable)
        size_t wptr = 1;
        serializeTight<bool>(true, reply, &wptr);
        return wptr; 
      }
    // -------------------- Requesting info on a particular link 
    case SKEY_LINKINFO_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_LINKINFO_RES;
        // collect the index, 
        uint8_t index = 0b00011111 & data[1];
        if(index < rt->linkCount && rt->links[index] != nullptr){
          size_t wptr = 1;
          serializeTight<char*>(rt->links[index]->typeName, reply, &wptr);
          serializeTight<char*>(rt->links[index]->name, reply, &wptr);
          // B1 also contains state info, 
          reply[1] |= (rt->links[index]->isOpen() ? 1 : 0) << 5;
          // that's all, 
          return wptr;
        } else {
          reply[1] = 0;
          return 2;
        }
      }
    // -------------------- Requesting info on a particular bus 
    case SKEY_BUSINFO_REQ:
      // TODO: busses, lol 
      OSAP_DEBUG("bus-fwds key in the runtime...");
      return 0;
    // -------------------- Requesting info on a particular port 
    case SKEY_PORTINFO_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_LINKINFO_RES;
        // collect the index, 
        uint16_t index = (uint16_t)(0b00000011 & data[1]) << 8 | data[2];
        if(index < rt->portCount && rt->ports[index] != nullptr){
          size_t wptr = 1;
          serializeTight<char*>(rt->ports[index]->typeName, reply, &wptr);
          serializeTight<char*>(rt->ports[index]->name, reply, &wptr);
          // OSAP_DEBUG(String("port type, name: \n" + String(ports[index]->typeName) + " \n" + String(ports[index]->name)));
          return wptr;
        } else {
          reply[1] = 0;
          return 2;
        }
      }
    // -------------------- Time service 
    case SKEY_TIME_CONFIG_GET_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_TIME_CONFIG_GET_RES; 
        // let's get underlying, system, and skew 
        uint64_t underlying = micros64();
        uint64_t system = rt->getSystemMicroseconds();
        fpint64_t skew = rt->clockSkew;
        size_t wptr = 1;
        serializeTight<uint64_t>(underlying, reply, &wptr);
        serializeTight<uint64_t>(system, reply, &wptr);
        // this serialization should be OK since it will not be -ve ? 
        serializeTight<uint64_t>(skew, reply, &wptr);
        return wptr;
      }
    case SKEY_TIME_CONFIG_SET_REQ:
      {
        reply[0] = 0 | PKEY_SMSG << 6 | SKEY_TIME_CONFIG_SET_RES;
        // 
        size_t rptr = 1; 
        // in here we have, 
        uint64_t setBaseUpdate = deserializeTight<uint64_t>(data, &rptr);
        float setSkew = deserializeTight<float>(data, &rptr);
        float setFilterAlpha = deserializeTight<float>(data, &rptr);
        float setPTerm = deserializeTight<float>(data, &rptr);
        bool setUseJumps = deserializeTight<bool>(data, &rptr);
        // now we do a little bit of logic / conversion, 
        // TODO: we should be able to update these selectively ... 
        if(setBaseUpdate != 0){
          rt->setSystemMicroseconds(setBaseUpdate);
          rt->lastHardReset = micros64();
        }
        if(setSkew != 0.0F){
          rt->clockSkew = fp_float32ToFixed64(setSkew);
        }
        rt->propFilterAlpha = fp_float32ToFixed64(setFilterAlpha);
        rt->propFilterOneMinusAlpha = fp_int64ToFixed64(1) - rt->propFilterAlpha;
        rt->clockSkewProportionalTerm = fp_float32ToFixed64(setPTerm);
        rt->useHardOffsetJumps = setUseJumps; 
        // let's also reset our (filtered) prop term:
        rt->propTerm = fp_int64ToFixed64(0);
        return 2;
      }
      break; 

    // -------------------- Results - not handled in embedded at the moment 
    case SKEY_RTINFO_RES:
    case SKEY_MTYPEGET_RES:
    case SKEY_MNAMEGET_RES:
    case SKEY_MNAMESET_RES:
    case SKEY_LINKINFO_RES:
    case SKEY_BUSINFO_RES:
    case SKEY_PORTINFO_RES:
      OSAP_ERROR("SMSG_RES in the embedded runtime, tf?");
      return 0;
    // -------------------- Mistakes 
    default:
      OSAP_ERROR("unknown key in the smsg switch " + String(data[0] & 0b00011111));
      return 0;
  }
}