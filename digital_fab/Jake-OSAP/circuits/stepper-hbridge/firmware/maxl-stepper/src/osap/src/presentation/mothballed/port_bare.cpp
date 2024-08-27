// integration of a simple port that ingests raw-byte type packet handlers 
/*
#include "port_bare.h"

OSAP_Port::OSAP_Port(
  const char* _name, 
  size_t (*_onMsgFunction)(uint8_t* data, size_t len, uint8_t* reply)
  ) : VPort(OSAP_Runtime::getInstance(), "bareWithAck", _name)
{
  onMsgFunctionWithReply = _onMsgFunction;
}

OSAP_Port::OSAP_Port(
  const char* _name, 
  void (*_onMsgFunction)(uint8_t* data, size_t len)
  ) : VPort(OSAP_Runtime::getInstance(), "bare", _name)
{
  onMsgFunctionWithoutReply = _onMsgFunction;
}

void OSAP_Port::onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort){
  // hand the data str8 to the handler, 
  if(onMsgFunctionWithReply != nullptr){
    // when given a reply mechanic, we send bytes back to the transmitter, 
    size_t replyLen = onMsgFunctionWithReply(data, len, _payload);
    send(_payload, replyLen, sourceRoute, sourcePort);
  } else {
    // otherwise we just absorb and bail 
    onMsgFunctionWithoutReply(data, len);
  }
}
*/