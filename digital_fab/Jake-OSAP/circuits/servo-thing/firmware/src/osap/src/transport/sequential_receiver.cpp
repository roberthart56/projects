#include "sequential_receiver.h"
#include "../utils/keys.h"
#include "../utils/debug.h"

OSAP_Sequential_Receiver::OSAP_Sequential_Receiver(const char* _typeName, const char* _name) : VPort(OSAP_Runtime::getInstance(), _typeName, _name) {};

void OSAP_Sequential_Receiver::onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort){
  if(data[0] != TKEY_SEQUENTIAL_TX){
    OSAP_ERROR("rx'd oddball TKEY at sequence rx'er");
    return; 
  }

  uint8_t msgID = data[1];
  size_t replyLen = onData(data + 2, len - 2, sourceRoute, sourcePort, _payload + 2); 

  // stuff our info, 
  _payload[0] = TKEY_SEQUENTIAL_RX;
  _payload[1] = msgID; 

  // and ship that back out, 
  #warning memory swappage needs more consideration; do we have race cond?
  send(_payload, replyLen + 2, sourceRoute, sourcePort);
}

size_t OSAP_Sequential_Receiver::onData(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort, uint8_t* reply){
  return 0;
}
