// pipe-er 
/*
#include "port_pipe.h"

OSAP_Port_Pipe::OSAP_Port_Pipe(const char* _name)
  :VPort(OSAP_Runtime::getInstance(), "pipe", _name){}

void OSAP_Port_Pipe::onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort){
  // readptr 
  uint16_t rptr = 0;
  switch(data[rptr ++]){
    case PONEPIPE_SETUP:
      {
        // we've rx'd a message from our partner port, wherence we will be sending 
        // msgs to in the future 
        portNumberAtReciever = sourcePort;
        // and stash flipped route, 
        routeToReciever.encodedPathLen = sourceRoute->encodedPathLen;
        routeToReciever.timeToLive = sourceRoute->timeToLive;
        routeToReciever.maxSegmentSize = sourceRoute->maxSegmentSize;
        // then the actual... route (no memory guards lol good luck)
        memcpy(routeToReciever.encodedPath, &(sourceRoute->encodedPath), routeToReciever.encodedPathLen);
        // then reply w/ an ack... 
        outBuffer[0] = PONEPIPE_SETUP_RES;
        send(outBuffer, 1, sourceRoute, sourcePort);
      }
      // then we done baby, 
      break;
  }
}

void OSAP_Port_Pipe::write(uint8_t* data, size_t len){
  // blind failure, beware !
  // could do...if not clear, stuff sample into datagram until are clear 
  if(!clearToSend()) return;
  // stuff it and... 
  uint16_t wptr = 0;
  outBuffer[wptr ++] = PONEPIPE_MSG;
  if(len > 128) len = 128;
  memcpy(outBuffer + 1, data, len);
  wptr += len; 
  send(outBuffer, wptr, &routeToReciever, portNumberAtReciever);
  // we're done, lol ? x
}
*/